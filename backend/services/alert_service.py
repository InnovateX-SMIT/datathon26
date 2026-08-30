import json
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import date, timedelta
from typing import List, Optional, Dict, Any

from backend.core.logging import logger
from backend.models.alert import Alert
from backend.models.recommendation import Recommendation, ResourceAllocation
from backend.models.crime import CrimeEvent
from backend.models.location import Location
from backend.repositories.alert_repository import AlertRepository
from backend.schemas.alert import AlertCreate
from backend.services.network_analytics_service import NetworkAnalyticsService

class AlertService:
    def __init__(self, db: Session, session_id: Optional[str] = None):
        self.db = db
        self.session_id = session_id
        self.repo = AlertRepository(db)

    def generate_alerts_from_intelligence(self) -> List[Alert]:
        """
        Runs the platform operational rules engine to convert predictions, networks,
        geo-stats, and pending recommendations into real-time alerts.
        """
        from backend.core.dataset_resolver import DatasetResolver
        active_id = DatasetResolver(self.db, self.session_id).get_active_dataset_id()
        schema_type = DatasetResolver(self.db, self.session_id).get_active_dataset_schema_type()
        
        alerts_to_create = []
        seen_identifiers = set()
        active_statuses = ["NEW", "ACKNOWLEDGED", "IN_PROGRESS"]

        # Helper to safely stage alerts with deterministic deduplication
        def stage_alert(alert_type: str, title: str, description: str, severity: str, source: str, crime_event_id: Optional[int] = None, metadata: Optional[dict] = None, dedup_suffix: str = ""):
            # Form unique key for in-memory deduplication based on Alert Type, Title, and suffix
            key = (alert_type, title, dedup_suffix)
            if key in seen_identifiers:
                return

            seen_identifiers.add(key)

            # Check database for active duplicates
            if not self.repo.check_alert_exists(title, description, active_statuses):
                alerts_to_create.append(AlertCreate(
                    crime_event_id=crime_event_id,
                    alert_type=alert_type,
                    title=title,
                    description=description,
                    severity=severity,
                    source=source,
                    status="NEW",
                    metadata_payload=json.dumps(metadata) if metadata else None
                ))

        # ==========================================
        # 1. TEMPORAL AND STATISTICAL ANALYTICS SETUP
        # ==========================================
        # Determine active date anchors
        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_geography import District
            from backend.models.fir_organization import Unit
            from backend.models.fir_law import CrimeHead
            
            max_date = self.db.query(func.max(CaseMaster.CrimeRegisteredDate)).filter(CaseMaster.dataset_id == active_id).scalar()
            anchor_date = max_date if max_date is not None else date.today()
            start_date = anchor_date - timedelta(days=180)
            
            raw_data = self.db.query(
                CaseMaster.CrimeRegisteredDate,
                District.name.label("district"),
                CrimeHead.CrimeGroupName.label("crime_type"),
                func.count(CaseMaster.id).label("count")
            ).select_from(CaseMaster)\
             .join(Unit, CaseMaster.PoliceStationID == Unit.id)\
             .join(District, Unit.DistrictID == District.id)\
             .join(CrimeHead, CaseMaster.CrimeMajorHeadID == CrimeHead.id)\
             .filter(
                 CaseMaster.dataset_id == active_id,
                 CaseMaster.CrimeRegisteredDate >= start_date,
                 CaseMaster.CrimeRegisteredDate <= anchor_date
             ).group_by(
                 CaseMaster.CrimeRegisteredDate,
                 District.name,
                 CrimeHead.CrimeGroupName
             ).all()
        else:
            max_date = self.db.query(func.max(CrimeEvent.crime_date)).filter(CrimeEvent.dataset_id == active_id).scalar()
            anchor_date = max_date if max_date is not None else date.today()
            start_date = anchor_date - timedelta(days=180)
            
            raw_data = self.db.query(
                CrimeEvent.crime_date,
                Location.district.label("district"),
                CrimeEvent.crime_type.label("crime_type"),
                func.count(CrimeEvent.id).label("count")
            ).select_from(CrimeEvent)\
             .join(Location, CrimeEvent.location_id == Location.id)\
             .filter(
                 CrimeEvent.dataset_id == active_id,
                 CrimeEvent.crime_date >= start_date,
                 CrimeEvent.crime_date <= anchor_date
             ).group_by(
                 CrimeEvent.crime_date,
                 Location.district,
                 CrimeEvent.crime_type
             ).all()

        # Organize counts by (district, crime_type) and date
        series = {}
        for row in raw_data:
            dt, dist, ctype, count = row
            if not dt or not dist or not ctype:
                continue
            key = (dist, ctype)
            if key not in series:
                series[key] = {}
            series[key][dt] = count

        # ==========================================
        # 2. CRIME SPIKE ALERTS
        # ==========================================
        # Compare current 30-day window against preceding 60-day average baseline
        for (dist, ctype), dates_dict in series.items():
            current_days = [anchor_date - timedelta(days=i) for i in range(30)]
            current_count = sum(dates_dict.get(d, 0) for d in current_days)
            
            baseline_days = [anchor_date - timedelta(days=i) for i in range(30, 90)]
            baseline_total = sum(dates_dict.get(d, 0) for d in baseline_days)
            baseline_avg = baseline_total / 2.0
            
            # Require minimum current count to avoid noise
            if current_count >= 5:
                percentage_change = 0.0
                if baseline_avg > 0:
                    percentage_change = ((current_count - baseline_avg) / baseline_avg) * 100.0
                else:
                    percentage_change = 100.0
                
                if percentage_change >= 50.0:
                    # Severity logic: CRITICAL for spikes >= 200% with high volume, HIGH for >= 100%, MEDIUM for >= 50%
                    if percentage_change >= 200.0 and current_count >= 15:
                        severity = "CRITICAL"
                    elif percentage_change >= 100.0:
                        severity = "HIGH"
                    else:
                        severity = "MEDIUM"
                    
                    dedup_week = anchor_date.strftime("%Y-%W")
                    stage_alert(
                        alert_type="crime_spike",
                        title=f"Crime Spike Detected: {ctype} in {dist}",
                        description=(
                            f"Significant increase in {ctype} incidents detected in {dist}. "
                            f"Current monthly count: {current_count} (vs. historical baseline of {baseline_avg:.1f}). "
                            f"Change: +{percentage_change:.1f}% over the last 30 days."
                        ),
                        severity=severity,
                        source="crime_analytics",
                        metadata={
                            "explanation": f"Current burglary count is {percentage_change:.1f}% above historical baseline.",
                            "evidence": {
                                "district": dist,
                                "crime_type": ctype,
                                "current_count": current_count,
                                "historical_baseline": round(baseline_avg, 2),
                                "percentage_change": round(percentage_change, 2),
                                "reporting_period": "Last 30 Days"
                            }
                        },
                        dedup_suffix=f"{dist}-{ctype}-{dedup_week}"
                    )

        # ==========================================
        # 3. STATISTICAL ANOMALY ALERTS
        # ==========================================
        # Calculate rolling Z-scores on weekly aggregates
        for (dist, ctype), dates_dict in series.items():
            date_keys = list(dates_dict.keys())
            if not date_keys or (max(date_keys) - min(date_keys)).days < 28:
                # Insufficient historical data for anomaly detection
                continue
            
            weekly_counts = []
            for w in range(25): # Current week + 24 historical weeks
                week_days = [anchor_date - timedelta(days=i) for i in range(w*7, (w+1)*7)]
                w_count = sum(dates_dict.get(d, 0) for d in week_days)
                weekly_counts.append(w_count)
            
            current_week_val = weekly_counts[0]
            hist_weeks_vals = weekly_counts[1:]
            
            import math
            hist_mean = sum(hist_weeks_vals) / len(hist_weeks_vals)
            variance = sum((x - hist_mean) ** 2 for x in hist_weeks_vals) / len(hist_weeks_vals)
            hist_std = math.sqrt(variance)
            
            z_score = 0.0
            if hist_std > 0:
                z_score = (current_week_val - hist_mean) / hist_std
            
            if z_score >= 1.75 and current_week_val >= 3:
                severity = "CRITICAL" if z_score >= 3.0 else "HIGH" if z_score >= 2.0 else "MEDIUM"
                dedup_week = anchor_date.strftime("%Y-%W")
                stage_alert(
                    alert_type="anomaly",
                    title=f"Statistical Anomaly: {ctype} in {dist}",
                    description=(
                        f"A statistical anomaly in {ctype} has been detected in {dist}. "
                        f"Current week count: {current_week_val} (vs. historical weekly mean of {hist_mean:.1f} ± {hist_std:.1f}). "
                        f"Z-score: {z_score:.2f}."
                    ),
                    severity=severity,
                    source="statistical_anomaly",
                    metadata={
                        "explanation": f"Observed anomaly based on standard deviation deviation. Z = {z_score:.2f}",
                        "evidence": {
                            "district": dist,
                            "crime_type": ctype,
                            "current_week_count": current_week_val,
                            "historical_mean": round(hist_mean, 2),
                            "standard_deviation": round(hist_std, 2),
                            "z_score": round(z_score, 2)
                        }
                    },
                    dedup_suffix=f"{dist}-{ctype}-{dedup_week}"
                )

        # ==========================================
        # 4. PREDICTED HOTSPOT ALERTS
        # ==========================================
        # Call PredictionService().predict_future_hotspots
        try:
            from backend.services.prediction_service import PredictionService
            pred_service = PredictionService()
            
            # Fetch active district mappings (IDs + Names)
            if schema_type == "fir_normalized":
                districts_query = self.db.query(District.id, District.name).select_from(CaseMaster)\
                    .join(Unit, CaseMaster.PoliceStationID == Unit.id)\
                    .join(District, Unit.DistrictID == District.id)\
                    .filter(CaseMaster.dataset_id == active_id)\
                    .distinct().all()
            else:
                districts_query = self.db.query(Location.id, Location.district).select_from(CrimeEvent)\
                    .join(Location, CrimeEvent.location_id == Location.id)\
                    .filter(CrimeEvent.dataset_id == active_id)\
                    .distinct().all()
            
            for d_id, d_name in districts_query:
                if not d_name:
                    continue
                dist_series = [dates_dict for (dist, ctype), dates_dict in series.items() if dist == d_name]
                
                p7 = sum(sum(dates_dict.get(anchor_date - timedelta(days=i), 0) for i in range(7)) for dates_dict in dist_series)
                p30 = sum(sum(dates_dict.get(anchor_date - timedelta(days=i), 0) for i in range(30)) for dates_dict in dist_series)
                p90 = sum(sum(dates_dict.get(anchor_date - timedelta(days=i), 0) for i in range(90)) for dates_dict in dist_series)
                p180 = sum(sum(dates_dict.get(anchor_date - timedelta(days=i), 0) for i in range(180)) for dates_dict in dist_series)
                
                pred_res = pred_service.predict_future_hotspots(
                    district_id=d_id,
                    prior_7d_crime_count=p7,
                    prior_30d_crime_count=p30,
                    prior_90d_crime_count=p90,
                    prior_180d_crime_count=p180
                )
                
                if pred_res:
                    dedup_week = anchor_date.strftime("%Y-%W")
                    if "predicted_hotspots" in pred_res:
                        # Fallback heuristic engine format
                        for hs in pred_res["predicted_hotspots"]:
                            # Filter to current district, or generate if dataset is small
                            if hs.get("district", "").upper() == d_name.upper() or len(districts_query) <= 2:
                                confidence = hs.get("risk_score")
                                stage_alert(
                                    alert_type="predicted_hotspot",
                                    title=f"Predicted Future Hotspot: {d_name}",
                                    description=(
                                        f"High-risk geographic hotspot predicted for {d_name} based on "
                                        f"historical trends and spatial density ratio."
                                    ),
                                    severity="HIGH" if confidence and confidence >= 0.80 else "MEDIUM",
                                    source="prediction",
                                    metadata={
                                        "explanation": f"Predicted hotspot based on available model output from {pred_res['source']}.",
                                        "evidence": {
                                            "district": d_name,
                                            "risk_score": confidence,
                                            "peak_window": hs.get("peak_window"),
                                            "forecasted_incidents_7d": hs.get("forecasted_incidents_7d")
                                        }
                                    },
                                    dedup_suffix=f"{d_name}-{dedup_week}"
                                )
                    elif pred_res.get("hotspot_flag") == "FUTURE_HOTSPOT":
                        # Primary Catalyst QuickML format
                        confidence = pred_res.get("confidence")
                        stage_alert(
                            alert_type="predicted_hotspot",
                            title=f"Predicted Future Hotspot: {d_name}",
                            description=(
                                f"CatBoost Classifier model predicted {d_name} as a future high-risk crime hotspot."
                            ),
                            severity="CRITICAL" if confidence and confidence >= 0.90 else "HIGH",
                            source="prediction",
                            metadata={
                                "explanation": f"Predicted hotspot based on available model output from {pred_res['source']}.",
                                "evidence": {
                                    "district": d_name,
                                    "confidence": confidence,
                                    "top_contributing_factors": pred_res.get("top_contributing_factors")
                                }
                            },
                            dedup_suffix=f"{d_name}-{dedup_week}"
                        )
        except Exception as e:
            logger.error(f"Error executing predicted hotspot model inference: {e}")

        # ==========================================
        # 5. HIGH-RISK OFFENDER ALERTS
        # ==========================================
        # Call PredictionService().predict_recidivism
        try:
            from backend.services.prediction_service import PredictionService
            pred_service = PredictionService()
            
            if schema_type == "fir_normalized":
                from backend.models.fir_people import Accused
                accused_query = self.db.query(
                    Accused.AccusedName, Accused.AgeYear, Accused.GenderID, Accused.PersonID,
                    CaseMaster.GravityOffenceID, CaseMaster.CrimeMajorHeadID, CaseMaster.CrimeMinorHeadID, CaseMaster.PoliceStationID
                ).join(CaseMaster, Accused.CaseMasterID == CaseMaster.id)\
                 .filter(CaseMaster.dataset_id == active_id).limit(10).all()
                
                for name, age, gender_id, person_id, grav, cmaj, cmin, ps_id in accused_query:
                    if not name:
                        continue
                    pred_res = pred_service.predict_recidivism(
                        age_years=age if age else 25,
                        gender_id=gender_id if gender_id else 1,
                        police_station_id=ps_id if ps_id else 1,
                        initial_gravity_offence_id=grav if grav else 2,
                        initial_crime_major_head_id=cmaj if cmaj else 2,
                        initial_crime_minor_head_id=cmin if cmin else 12
                    )
                    
                    if pred_res and pred_res.get("recidivism_flag") == "REPEAT_OFFENDER":
                        confidence = pred_res.get("confidence")
                        subject_id = person_id if person_id else f"ACC-{(id(name) % 100000):05d}"
                        
                        stage_alert(
                            alert_type="high_risk_offender",
                            title=f"High-Risk Offender Signal: Subject {subject_id}",
                            description=(
                                f"High-risk prediction based on available model output. "
                                f"Subject exhibits behavioral indicators associated with repeat offenses."
                            ),
                            severity="HIGH" if confidence and confidence >= 0.75 else "MEDIUM",
                            source="prediction",
                            metadata={
                                "explanation": f"High-risk prediction based on available model output from {pred_res.get('source')}.",
                                "evidence": {
                                    "subject_identifier": subject_id,
                                    "confidence": confidence,
                                    "top_contributing_factors": pred_res.get("top_contributing_factors")
                                }
                            },
                            dedup_suffix=subject_id
                        )
            else:
                from backend.models.criminal import Criminal
                criminal_query = self.db.query(
                    Criminal.id, Criminal.name, Criminal.age, Criminal.gender, Criminal.risk_score
                ).filter(Criminal.dataset_id == active_id).limit(10).all()
                
                for c_id, name, age, gender, risk_score in criminal_query:
                    gender_id = 1 if gender == "Male" else 2
                    pred_res = pred_service.predict_recidivism(
                        age_years=int(age) if age else 25,
                        gender_id=gender_id,
                        initial_gravity_offence_id=2
                    )
                    
                    if pred_res and (pred_res.get("recidivism_flag") == "REPEAT_OFFENDER" or risk_score >= 0.70):
                        confidence = pred_res.get("confidence") or risk_score
                        subject_id = f"CRM-{c_id:05d}"
                        
                        stage_alert(
                            alert_type="high_risk_offender",
                            title=f"High-Risk Offender Signal: Subject {subject_id}",
                            description=(
                                f"High-risk prediction based on available model output. "
                                f"Subject exhibits behavioral indicators associated with repeat offenses."
                            ),
                            severity="HIGH" if confidence >= 0.75 else "MEDIUM",
                            source="prediction",
                            metadata={
                                "explanation": f"High-risk prediction based on available model output from {pred_res.get('source')}.",
                                "evidence": {
                                    "subject_identifier": subject_id,
                                    "confidence": confidence,
                                    "top_contributing_factors": pred_res.get("top_contributing_factors")
                                }
                            },
                            dedup_suffix=subject_id
                        )
        except Exception as e:
            logger.error(f"Error executing high-risk offender prediction: {e}")

        # ==========================================
        # 6. SIMILAR MO ALERTS
        # ==========================================
        # Call ModusOperandiService().get_cross_jurisdiction_patterns
        try:
            from backend.analytics.crime_analysis.modus_operandi_service import ModusOperandiService
            mo_service = ModusOperandiService(self.db, self.session_id)
            
            summary = mo_service.get_cross_jurisdiction_patterns(min_similarity=0.50, limit=5)
            links = getattr(summary, "sample_links", [])
            for link in links:
                case_a = getattr(link, "source_case_id", None)
                case_b = getattr(link, "target_case_id", None)
                score = getattr(link, "similarity_score", None)
                crime_type = getattr(link, "crime_type", None) or "Incident Group"
                
                if score and score >= 0.50:
                    score_percent = int(round(score * 100))
                    stage_alert(
                        alert_type="similar_mo",
                        title=f"Similar MO Pattern Detected: Case #{case_a} & Case #{case_b}",
                        description=(
                            f"Modus Operandi analysis detected matching crime pattern ({score_percent}%) "
                            f"between Case #{case_a} and Case #{case_b} of type {crime_type} across districts."
                        ),
                        severity="HIGH" if score >= 0.75 else "MEDIUM",
                        source="mo_intelligence",
                        crime_event_id=case_a,
                        metadata={
                            "explanation": f"Behavioral similarity indicates matching crime patterns and potential investigative leads.",
                            "evidence": {
                                "related_cases": [case_a, case_b],
                                "crime_type": crime_type,
                                "similarity_score": round(score, 4),
                                "similarity_percentage": score_percent
                            }
                        },
                        dedup_suffix=f"{case_a}-{case_b}"
                    )
        except Exception as e:
            logger.error(f"Error executing Modus Operandi similarity analysis: {e}")

        # ==========================================
        # 7. CRIMINAL NETWORK ALERTS
        # ==========================================
        # Call NetworkAnalyticsService centrality, clusters, and repeat associations
        try:
            net_service = NetworkAnalyticsService(self.db)
            
            # Centrality discovery
            centrality = net_service.get_centrality(limit=5)
            for item in centrality.get("betweenness", []):
                if item["type"] == "criminal" and item["score"] >= 0.15:
                    stage_alert(
                        alert_type="criminal_network",
                        title="Network Centrality Alert: Key Suspect Bridge Identified",
                        description=(
                            f"Potential association requiring review: key structural bridge offender "
                            f"'{item['label']}' identified (betweenness centrality: {item['score']:.2f})."
                        ),
                        severity="HIGH",
                        source="network",
                        metadata={
                            "explanation": "High-centrality suspect requiring review.",
                            "evidence": {
                                "suspect_id": item["id"],
                                "suspect_label": item["label"],
                                "betweenness_centrality": round(item["score"], 4)
                            }
                        },
                        dedup_suffix=str(item["id"])
                    )

            # Cluster/Gang discovery
            clusters = net_service.get_clusters()
            for cluster in clusters:
                if cluster["criminal_count"] >= 3 and cluster["size"] >= 5:
                    stage_alert(
                        alert_type="criminal_network",
                        title=f"Potential Criminal Association: Gang Cluster {cluster['cluster_id']}",
                        description=(
                            f"Network relationship detected: cluster with {cluster['criminal_count']} co-offenders "
                            f"across {cluster['crime_count']} crime events."
                        ),
                        severity="CRITICAL",
                        source="network",
                        metadata={
                            "explanation": "Network relationship detected. Requires investigative review.",
                            "evidence": {
                                "cluster_id": cluster["cluster_id"],
                                "size": cluster["size"],
                                "criminal_count": cluster["criminal_count"],
                                "crime_count": cluster["crime_count"]
                            }
                        },
                        dedup_suffix=str(cluster["cluster_id"])
                    )
            
            # Repeat co-offending associations
            repeat_assocs = net_service.get_repeat_associations(limit=5)
            for assoc in repeat_assocs:
                freq = assoc.get("frequency", 0) or assoc.get("shared_crimes_count", 0)
                strength = assoc.get("strength", 0.0)
                crim_a = assoc.get("criminal_a", {})
                crim_b = assoc.get("criminal_b", {})
                
                if freq >= 2 and strength >= 0.25:
                    stage_alert(
                        alert_type="criminal_network",
                        title=f"Potential Criminal Association: {crim_a.get('label')} & {crim_b.get('label')}",
                        description=(
                            f"Strong co-offending association discovered between {crim_a.get('label')} "
                            f"and {crim_b.get('label')} with {freq} shared crime events."
                        ),
                        severity="HIGH",
                        source="network",
                        metadata={
                            "explanation": "Potential association identified. Requires investigative review.",
                            "evidence": {
                                "criminal_a": crim_a.get("label"),
                                "criminal_b": crim_b.get("label"),
                                "shared_crimes_count": freq,
                                "association_strength": round(strength, 4)
                            }
                        },
                        dedup_suffix=f"{crim_a.get('id')}-{crim_b.get('id')}"
                    )
        except Exception as e:
            logger.error(f"Error executing criminal network analytics: {e}")

        # ==========================================
        # 8. DECISION SUPPORT ALERTS
        # ==========================================
        if schema_type == "fir_normalized":
            unresolved_recs = self.db.query(Recommendation).filter(
                Recommendation.status == "pending",
                Recommendation.priority == "high"
            ).limit(10).all()
        else:
            unresolved_recs = self.db.query(Recommendation).outerjoin(CrimeEvent).filter(
                (CrimeEvent.dataset_id == active_id) | (Recommendation.crime_event_id.is_(None)),
                Recommendation.status == "pending",
                Recommendation.priority == "high"
            ).limit(10).all()
 
        for rec in unresolved_recs:
            stage_alert(
                alert_type="decision_support",
                title="Pending High Priority Action",
                description=f"Unresolved critical recommendation: {rec.recommendation_text}",
                severity="HIGH",
                source="decision_support",
                crime_event_id=rec.crime_event_id,
                metadata={"recommendation_id": rec.id},
                dedup_suffix=str(rec.id)
            )
 
        # Personnel shortage / resource imbalance alerts
        allocations = self.db.query(ResourceAllocation).order_by(ResourceAllocation.created_at.desc()).limit(5).all()
        for alloc in allocations:
            try:
                solved_data = json.loads(alloc.solved_allocation)
                for beat in solved_data:
                    severity = beat.get("normalized_severity", 0.0)
                    total_staff = beat.get("asi_allocated", 0) + beat.get("chc_allocated", 0) + beat.get("cpc_allocated", 0)
                    if severity >= 0.40 and total_staff < 5:
                        stage_alert(
                            alert_type="decision_support",
                            title="Resource Allocation Staffing Deficit",
                            description=f"Shortage in district '{alloc.district}': Beat '{beat.get('beat_name')}' has severity {severity * 100:.1f}% but only {total_staff} staff allocated.",
                            severity="HIGH",
                            source="decision_support",
                            metadata={"district": alloc.district, "beat_name": beat.get("beat_name"), "severity": severity},
                            dedup_suffix=f"{alloc.district}-{beat.get('beat_name')}"
                        )
            except Exception:
                pass

        # Bulk write all newly staged alerts
        if alerts_to_create:
            return self.repo.create_alerts_bulk(alerts_to_create)
        return []

    def get_alerts(self, severity: Optional[str] = None, status: Optional[str] = None, source: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Alert]:
        from backend.core.dataset_resolver import DatasetResolver
        active_ids = DatasetResolver(self.db, self.session_id).get_active_dataset_ids_optional()
        if not active_ids:
            return []
        return self.repo.get_alerts(severity=severity, status=status, source=source, skip=skip, limit=limit)

    def get_alert_by_id(self, alert_id: int) -> Optional[Alert]:
        return self.repo.get_alert_by_id(alert_id)

    def update_alert_status(self, alert_id: int, status_str: str, assigned_user_id: Optional[int] = None) -> Optional[Alert]:
        return self.repo.update_alert_status(alert_id, status=status_str, assigned_user_id=assigned_user_id)

    def get_summary(self) -> Dict[str, Any]:
        from backend.core.dataset_resolver import DatasetResolver
        active_ids = DatasetResolver(self.db, self.session_id).get_active_dataset_ids_optional()
        if not active_ids:
            return {
                "total_alerts": 0,
                "active_alerts": 0,
                "critical_anomalies": 0,
                "resolved_alerts": 0,
                "todays_alerts": 0,
                "by_severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
                "by_status": {"NEW": 0, "ACKNOWLEDGED": 0, "IN_PROGRESS": 0, "RESOLVED": 0},
                "by_source": {"geo": 0, "temporal": 0, "network": 0, "decision_support": 0}
            }
        return self.repo.get_alert_summary_statistics()
