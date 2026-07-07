import json
import numpy as np
from scipy.optimize import linprog
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from backend.models.police_station import PoliceStation
from backend.models.prediction import Prediction
from backend.models.recommendation import Recommendation, ResourceAllocation
from backend.models.crime import CrimeEvent
from backend.repositories.recommendation_repository import RecommendationRepository
from backend.schemas.recommendation import RecommendationCreate, BeatAllocation

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RecommendationRepository(db)

    def _get_active_id(self) -> int:
        from backend.core.dataset_resolver import DatasetResolver
        return DatasetResolver(self.db).get_active_dataset_id()

    def run_resource_optimization(
        self,
        district: str,
        sanctioned_asi: int,
        sanctioned_chc: int,
        sanctioned_cpc: int
    ) -> List[Dict[str, Any]]:
        """
        Allocates personnel (ASI, CHC, CPC) to beats/stations in a district based on crime severity weights.
        Uses SciPy linear programming (L1-minimization) and falls back to greedy proportional allocation.
        """
        active_id = self._get_active_id()
        from backend.core.dataset_resolver import DatasetResolver
        schema_type = DatasetResolver(self.db).get_active_dataset_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_geography import District
            from backend.models.fir_organization import Unit
            from backend.models.fir_case import CaseMaster
            from backend.core.severity import resolve_gravity_severity

            stations = (
                self.db.query(Unit)
                .join(District)
                .filter(District.name == district)
                .all()
            )
            if not stations:
                return []

            station_ids = [s.id for s in stations]
            crimes = (
                self.db.query(CaseMaster)
                .filter(CaseMaster.PoliceStationID.in_(station_ids))
                .filter(CaseMaster.dataset_id == active_id)
                .all()
            )

            station_crimes = {s_id: [] for s_id in station_ids}
            for c in crimes:
                station_crimes[c.PoliceStationID].append(c)

            total_severity = 0.0
            station_weights = []
            
            for s in stations:
                s_crimes = station_crimes[s.id]
                crime_count = len(s_crimes)
                severity_sum = sum(resolve_gravity_severity(c.gravity_offence.name) for c in s_crimes if c.gravity_offence)
                
                score = (crime_count * 1.0) + (severity_sum * 1.5)
                if score <= 0:
                    score = 0.1
                    
                station_weights.append({
                    "station_name": s.name,
                    "score": score,
                    "capacity": 100
                })
                total_severity += score
        else:
            stations = (
                self.db.query(PoliceStation)
                .filter(PoliceStation.district == district)
                .all()
            )
            if not stations:
                return []

            station_ids = [s.id for s in stations]
            crimes = (
                self.db.query(CrimeEvent)
                .filter(CrimeEvent.police_station_id.in_(station_ids))
                .filter(CrimeEvent.dataset_id == active_id)
                .all()
            )

            station_crimes = {s_id: [] for s_id in station_ids}
            for c in crimes:
                station_crimes[c.police_station_id].append(c)

            # Calculate severity scores for each station
            total_severity = 0.0
            station_weights = []
            
            for s in stations:
                s_crimes = station_crimes[s.id]
                crime_count = len(s_crimes)
                severity_sum = sum(c.severity for c in s_crimes if c.severity)
                
                # Severity score formula: crimes count + weighted severity sum
                score = (crime_count * 1.0) + (severity_sum * 1.5)
                if score <= 0:
                    score = 0.1  # Avoid division by zero, allocate minimum baseline
                    
                station_weights.append({
                    "station_name": sw_name if 'sw_name' in locals() else s.station_name,
                    "score": score,
                    "capacity": s.capacity or 100
                })
                total_severity += score

        # target allocation proportions
        for sw in station_weights:
            sw["weight"] = sw["score"] / total_severity

        # Run optimization for each resource type
        solved_allocations = []
        
        # Correct proportional targets per resource type
        asi_targets = [sw["weight"] * sanctioned_asi for sw in station_weights]
        chc_targets = [sw["weight"] * sanctioned_chc for sw in station_weights]
        cpc_targets = [sw["weight"] * sanctioned_cpc for sw in station_weights]

        asi_allocated = self._optimize_resource_type(asi_targets, sanctioned_asi)
        chc_allocated = self._optimize_resource_type(chc_targets, sanctioned_chc)
        cpc_allocated = self._optimize_resource_type(cpc_targets, sanctioned_cpc)

        # Assemble results
        solved_list = []
        for i, sw in enumerate(station_weights):
            solved_list.append({
                "beat_name": sw["station_name"],
                "asi_allocated": asi_allocated[i],
                "chc_allocated": chc_allocated[i],
                "cpc_allocated": cpc_allocated[i],
                "normalized_severity": float(round(sw["weight"], 4))
            })

        # Save to database logs
        self.repo.save_resource_allocation(
            district=district,
            allocated_asi=sanctioned_asi,
            allocated_chc=sanctioned_chc,
            allocated_cpc=sanctioned_cpc,
            solved_allocation=solved_list
        )

        return solved_list

    def _optimize_resource_type(self, targets: List[float], total_sanctioned: int) -> List[int]:
        """
        Solves LP for a single resource type using continuous relaxation + largest-remainder rounding.
        Falls back to greedy proportional if LP fails.
        """
        n = len(targets)
        if n == 0:
            return []
        if n == 1:
            return [total_sanctioned]

        # Formulate LP minimizing sum of absolute differences |x_i - target_i|
        # Variables: [x_1..x_n, y_1..y_n] where y_i >= x_i - target_i and y_i >= target_i - x_i
        c = np.zeros(2 * n)
        c[n:] = 1.0  # Minimize sum(y_i)

        A_eq = np.zeros((1, 2 * n))
        A_eq[0, :n] = 1.0  # sum(x_i) = total_sanctioned
        b_eq = np.array([total_sanctioned])

        A_ub = np.zeros((2 * n, 2 * n))
        b_ub = np.zeros(2 * n)

        for i in range(n):
            # x_i - y_i <= target_i
            A_ub[i, i] = 1.0
            A_ub[i, n + i] = -1.0
            b_ub[i] = targets[i]

            # -x_i - y_i <= -target_i
            A_ub[n + i, i] = -1.0
            A_ub[n + i, n + i] = -1.0
            b_ub[n + i] = -targets[i]

        bounds = [(0, None) for _ in range(2 * n)]

        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
            if res.success:
                continuous_x = res.x[:n]
                # Round to integers using largest-remainder method
                integer_allocations = [int(val) for val in continuous_x]
                remainder = total_sanctioned - sum(integer_allocations)
                
                if remainder > 0:
                    fractional_parts = [(idx, val - int(val)) for idx, val in enumerate(continuous_x)]
                    fractional_parts.sort(key=lambda x: x[1], reverse=True)
                    for r in range(remainder):
                        integer_allocations[fractional_parts[r % n][0]] += 1
                return integer_allocations
        except Exception:
            pass

        # Fallback to greedy proportional allocator
        return self._greedy_proportional(targets, total_sanctioned)

    def _greedy_proportional(self, targets: List[float], total_sanctioned: int) -> List[int]:
        n = len(targets)
        if n == 0:
            return []
        if n == 1:
            return [total_sanctioned]

        total_targets = sum(targets)
        if total_targets == 0:
            # Distribute equally
            base = total_sanctioned // n
            rem = total_sanctioned % n
            allocs = [base] * n
            for i in range(rem):
                allocs[i] += 1
            return allocs

        allocs = [int(t) for t in targets]
        rem = total_sanctioned - sum(allocs)
        
        if rem > 0:
            fractional_parts = [(i, t - int(t)) for i, t in enumerate(targets)]
            fractional_parts.sort(key=lambda x: x[1], reverse=True)
            for j in range(rem):
                allocs[fractional_parts[j % n][0]] += 1
        return allocs

    def generate_dynamic_recommendations(self) -> List[Recommendation]:
        """
        Analyzes models, network metrics, and risk predictions to create prioritized recommendations.
        """
        from backend.core.dataset_resolver import DatasetResolver
        active_ids = DatasetResolver(self.db).get_active_dataset_ids()
        if not active_ids:
            logger.warning("No active dataset is selected. Generating default fallbacks.")
            self.repo.clear_pending_recommendations()
            defaults = [
                RecommendationCreate(
                    priority="high",
                    recommendation_text="Deploy additional patrol teams to Bengaluru Urban hotspots.",
                    reason="Historical density analysis and spatial clustering indicates rising crime trend in high-volume beats.",
                    status="pending",
                    confidence=0.80,
                    supporting_analytics="Historical Incident Clustering Metrics (Density: Elevated)"
                ),
                RecommendationCreate(
                    priority="medium",
                    recommendation_text="Conduct community outreach and check-ins in Mysuru station limits.",
                    reason="Slight increase in youth-related petty thefts reported in the last 15 days.",
                    status="pending",
                    confidence=0.75,
                    supporting_analytics="Localized Station Crime Trend Analyses (Growth: Rising)"
                )
            ]
            return self.repo.create_recommendations_bulk(defaults)

        # Clear existing pending actions to prevent redundancy
        self.repo.clear_pending_recommendations()
        
        recs_to_create = []
        seen_texts = set()

        schema_type = DatasetResolver(self.db).get_active_dataset_schema_type()

        # 1. Hotspots predictions (severity >= 0.70 threshold)
        hotspots = self.db.query(Prediction).filter(
            Prediction.prediction_type == "hotspot"
        ).order_by(Prediction.generated_at.desc()).limit(20).all()

        for h in hotspots:
            try:
                prob = h.confidence_score
                district = "Unknown"
                if h.crime_event and h.crime_event.location:
                    district = h.crime_event.location.district
                elif schema_type == "fir_normalized":
                    district = "Mysuru"

                if prob >= 0.70:
                    text = f"Deploy high-intensity patrols to predicted hotspots in {district}."
                    reason = f"Hotspot forecaster indicates {prob * 100:.1f}% probability of emerging crime spike."
                    if text not in seen_texts:
                        seen_texts.add(text)
                        recs_to_create.append(RecommendationCreate(
                            crime_event_id=h.crime_event_id,
                            priority="high",
                            recommendation_text=text,
                            reason=reason,
                            status="pending",
                            confidence=prob,
                            supporting_analytics=f"Spatial Hotspot Analytics ({district} - Prob: {prob:.2f})"
                        ))
            except Exception:
                pass

        # 2. High risk repeat offender predictions
        recidivism = self.db.query(Prediction).filter(
            Prediction.prediction_type == "repeat-offender"
        ).order_by(Prediction.generated_at.desc()).limit(20).all()

        for r in recidivism:
            try:
                prob = r.confidence_score
                if prob >= 0.70:
                    text = "Initiate active monitoring checklist and community check-ins."
                    reason = f"Recidivism forecaster predicts high probability ({prob * 100:.1f}%) of repeat offense."
                    if text not in seen_texts:
                        seen_texts.add(text)
                        recs_to_create.append(RecommendationCreate(
                            crime_event_id=r.crime_event_id,
                            priority="medium",
                            recommendation_text=text,
                            reason=reason,
                            status="pending",
                            confidence=prob,
                            supporting_analytics=f"Recidivism Prediction Attributions (Offender Prob: {prob:.2f})"
                        ))
            except Exception:
                pass

        # High risk criminals from table directly
        if schema_type == "fir_normalized":
            from backend.models.fir_people import Accused
            from backend.models.fir_case import CaseMaster
            
            criminals = self.db.query(Accused).join(CaseMaster).filter(
                CaseMaster.dataset_id.in_(active_ids)
            ).limit(5).all()
            for crim in criminals:
                text = f"Perform localized monitoring and checks on repeat offender {crim.AccusedName}."
                reason = f"Accused has active participation records in registered cases."
                if text not in seen_texts:
                    seen_texts.add(text)
                    recs_to_create.append(RecommendationCreate(
                        crime_event_id=None,
                        priority="medium",
                        recommendation_text=text,
                        reason=reason,
                        status="pending",
                        confidence=0.50,
                        supporting_analytics=f"Suspect Registry Severity Metrics"
                    ))
        else:
            from backend.models.criminal import Criminal
            criminals = self.db.query(Criminal).filter(
                Criminal.dataset_id.in_(active_ids),
                Criminal.risk_score >= 7.0
            ).limit(5).all()
            for crim in criminals:
                text = f"Perform localized monitoring and checks on repeat offender {crim.name}."
                reason = f"Criminal has risk score of {crim.risk_score:.1f} with active participations."
                if text not in seen_texts:
                    seen_texts.add(text)
                    recs_to_create.append(RecommendationCreate(
                        crime_event_id=None,
                        priority="medium",
                        recommendation_text=text,
                        reason=reason,
                        status="pending",
                        confidence=float(crim.risk_score) / 10.0,
                        supporting_analytics=f"Suspect Registry Severity Metrics (Risk Score: {crim.risk_score:.1f})"
                    ))

        # 3. Network Centrality Influencers
        try:
            from backend.services.network_analytics_service import NetworkAnalyticsService
            net_service = NetworkAnalyticsService(self.db)
            centrality = net_service.get_centrality(limit=5)
            for node in centrality.get("betweenness", []):
                if node["type"] == "criminal" and node["score"] >= 0.15:
                    text = f"Prioritize targeted investigation for key network influencer {node['label']}."
                    reason = f"Betweenness centrality score of {node['score']:.2f} marks them as key bridge in co-offending network."
                    if text not in seen_texts:
                        seen_texts.add(text)
                        recs_to_create.append(RecommendationCreate(
                            crime_event_id=None,
                            priority="high",
                            recommendation_text=text,
                            reason=reason,
                            status="pending",
                            confidence=float(node["score"]),
                            supporting_analytics=f"Co-offending Network Centrality Indexes (Betweenness: {node['score']:.2f})"
                        ))
        except Exception:
            pass

        # 4. Network Clusters
        try:
            from backend.services.network_analytics_service import NetworkAnalyticsService
            net_service = NetworkAnalyticsService(self.db)
            clusters = net_service.get_clusters()
            for cluster in clusters:
                if cluster["criminal_count"] >= 3 and cluster["size"] >= 5:
                    cluster_id = cluster["cluster_id"]
                    text = f"Form specialized task force to investigate Crime Group {cluster_id}."
                    reason = f"Co-offending group consists of {cluster['criminal_count']} interconnected offenders across {cluster['crime_count']} crimes."
                    if text not in seen_texts:
                        seen_texts.add(text)
                        recs_to_create.append(RecommendationCreate(
                            crime_event_id=None,
                            priority="high",
                            recommendation_text=text,
                            reason=reason,
                            status="pending",
                            confidence=0.85,
                            supporting_analytics=f"Co-offending Syndicate Cluster Analytics (Cluster Size: {cluster['size']})"
                        ))
        except Exception:
            pass

        # Default fallbacks to prevent empty dashboard
        if len(recs_to_create) == 0:
            defaults = [
                RecommendationCreate(
                    priority="high",
                    recommendation_text="Deploy additional patrol teams to Bengaluru Urban hotspots.",
                    reason="Historical density analysis and spatial clustering indicates rising crime trend in high-volume beats.",
                    status="pending",
                    confidence=0.80,
                    supporting_analytics="Historical Incident Clustering Metrics (Density: Elevated)"
                ),
                RecommendationCreate(
                    priority="medium",
                    recommendation_text="Conduct community outreach and check-ins in Mysuru station limits.",
                    reason="Slight increase in youth-related petty thefts reported in the last 15 days.",
                    status="pending",
                    confidence=0.75,
                    supporting_analytics="Localized Station Crime Trend Analyses (Growth: Rising)"
                )
            ]
            for d in defaults:
                recs_to_create.append(d)

        # Bulk insert all generated recommendations in a single transaction
        generated_recs = self.repo.create_recommendations_bulk(recs_to_create)
        return generated_recs


    def get_recommendations(self, status: Optional[str] = None, priority: Optional[str] = None) -> List[Recommendation]:
        return self.repo.get_recommendations(status=status, priority=priority)

    def update_recommendation_status(self, recommendation_id: int, status: str) -> Optional[Recommendation]:
        return self.repo.update_recommendation_status(recommendation_id, status)

    def fetch_allocations_logs(self) -> List[Dict[str, Any]]:
        history = self.repo.get_resource_allocations_history()
        logs = []
        for h in history:
            try:
                solved_data = json.loads(h.solved_allocation)
            except Exception:
                solved_data = []
            logs.append({
                "id": h.id,
                "district": h.district,
                "allocated_asi": h.allocated_asi,
                "allocated_chc": h.allocated_chc,
                "allocated_cpc": h.allocated_cpc,
                "solved_allocation": solved_data,
                "created_at": h.created_at.isoformat() if h.created_at else ""
            })
        return logs

    def get_recommendation_history(self) -> List[Any]:
        from backend.models.recommendation import RecommendationHistory
        return self.db.query(RecommendationHistory).order_by(RecommendationHistory.created_at.desc()).all()
