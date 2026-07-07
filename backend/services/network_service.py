from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List, Set
from backend.repositories.network_repository import NetworkRepository
from sqlalchemy import func

class NetworkService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = NetworkRepository(db)

    def _serialize_criminal(self, criminal) -> Dict[str, Any]:
        return {
            "id": f"criminal_{criminal.id}",
            "type": "criminal",
            "label": criminal.name,
            "metadata": {
                "gender": criminal.gender,
                "age": criminal.age,
                "occupation": criminal.occupation,
                "caste": criminal.caste,
                "risk_score": criminal.risk_score,
                "status": criminal.status
            }
        }

    def _serialize_crime(self, crime) -> Dict[str, Any]:
        return {
            "id": f"crime_{crime.id}",
            "type": "crime",
            "label": crime.crime_type,
            "metadata": {
                "crime_category": crime.crime_category,
                "crime_subcategory": crime.crime_subcategory,
                "severity": crime.severity,
                "status": crime.status,
                "crime_date": str(crime.crime_date) if crime.crime_date else None,
                "crime_time": str(crime.crime_time) if crime.crime_time else None
            }
        }

    def _serialize_location(self, location) -> Dict[str, Any]:
        return {
            "id": f"location_{location.id}",
            "type": "location",
            "label": f"{location.district}, {location.state}",
            "metadata": {
                "state": location.state,
                "district": location.district,
                "latitude": location.latitude,
                "longitude": location.longitude
            }
        }

    def _get_active_id(self) -> int:
        from backend.core.dataset_resolver import DatasetResolver
        return DatasetResolver(self.db).get_active_dataset_id()

    def _get_schema_type(self) -> str:
        from backend.core.dataset_resolver import DatasetResolver
        return DatasetResolver(self.db).get_active_dataset_schema_type()

    def get_sample_criminals(self, limit: int = 10) -> Dict[str, Any]:
        active_id = self._get_active_id()
        schema_type = self._get_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_people import Accused
            from backend.models.fir_case import CaseMaster
            accused_list = self.db.query(Accused).join(CaseMaster).filter(
                CaseMaster.dataset_id == active_id
            ).order_by(Accused.id.asc()).limit(limit).all()
            return {
                "dataset_id": active_id,
                "criminals": [
                    {
                        "id": acc.id,
                        "name": acc.AccusedName,
                        "risk_score": 5.0,
                        "status": "active"
                    }
                    for acc in accused_list
                ]
            }
        else:
            criminals = self.repo.get_sample_criminals(dataset_id=active_id, limit=limit)
            return {
                "dataset_id": active_id,
                "criminals": [
                    {
                        "id": criminal.id,
                        "name": criminal.name,
                        "risk_score": criminal.risk_score,
                        "status": criminal.status,
                    }
                    for criminal in criminals
                ],
            }

    def build_criminal_network(self, criminal_id: int) -> Optional[Dict[str, Any]]:
        active_id = self._get_active_id()
        schema_type = self._get_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_people import Accused
            from backend.models.fir_case import CaseMaster, Inv_OccuranceTime
            from backend.models.fir_geography import District, Unit
            
            acc = self.db.query(Accused).filter(Accused.id == criminal_id).first()
            if not acc:
                return None
                
            nodes = []
            edges = []
            seen_nodes = set()
            seen_edges = set()
            
            c_node_id = f"criminal_{acc.id}"
            nodes.append({
                "id": c_node_id,
                "type": "criminal",
                "label": acc.AccusedName,
                "metadata": {
                    "gender": acc.gender.name if acc.gender else "Male",
                    "age": acc.AgeYear,
                    "occupation": "Unknown",
                    "caste": "Unknown",
                    "risk_score": 5.0,
                    "status": "active"
                }
            })
            seen_nodes.add(c_node_id)
            
            # Find cases involving this accused by name matching
            cases_involved = self.db.query(CaseMaster).join(Accused).filter(
                Accused.AccusedName == acc.AccusedName,
                CaseMaster.dataset_id == active_id
            ).all()
            
            for case in cases_involved:
                crime_node_id = f"crime_{case.id}"
                if crime_node_id not in seen_nodes:
                    nodes.append({
                        "id": crime_node_id,
                        "type": "crime",
                        "label": case.crime_minor_head.CrimeHeadName if case.crime_minor_head else "Crime",
                        "metadata": {
                            "crime_category": case.crime_major_head.CrimeGroupName if case.crime_major_head else "General",
                            "crime_subcategory": case.crime_minor_head.CrimeHeadName if case.crime_minor_head else "General",
                            "severity": 5.0 if case.gravity_offence.name == "Heinous" else 2.0,
                            "status": case.case_status.name if case.case_status else "Under Investigation",
                            "crime_date": str(case.registered_date) if case.registered_date else None,
                            "crime_time": None
                        }
                    })
                    seen_nodes.add(crime_node_id)
                    
                edge_key = (c_node_id, crime_node_id, "INVOLVED_IN")
                if edge_key not in seen_edges:
                    edges.append({
                        "source": c_node_id,
                        "target": crime_node_id,
                        "relationship": "INVOLVED_IN"
                    })
                    seen_edges.add(edge_key)
                    
                # Occurrence District (Location)
                unit = self.db.query(Unit).filter(Unit.id == case.PoliceStationID).first()
                if unit and unit.DistrictID:
                    district = self.db.query(District).filter(District.id == unit.DistrictID).first()
                    if district:
                        loc_node_id = f"location_{district.id}"
                        if loc_node_id not in seen_nodes:
                            # Average coordinates for district
                            coords = self.db.query(
                                func.avg(Inv_OccuranceTime.latitude),
                                func.avg(Inv_OccuranceTime.longitude)
                            ).select_from(CaseMaster).join(Unit, CaseMaster.PoliceStationID == Unit.id).join(
                                Inv_OccuranceTime, Inv_OccuranceTime.CaseMasterID == CaseMaster.id
                            ).filter(Unit.DistrictID == district.id).first()
                            
                            lat = float(coords[0]) if coords and coords[0] is not None else 12.9716
                            lon = float(coords[1]) if coords and coords[1] is not None else 77.5946
                            
                            nodes.append({
                                "id": loc_node_id,
                                "type": "location",
                                "label": f"{district.name}, Karnataka",
                                "metadata": {
                                    "state": "Karnataka",
                                    "district": district.name,
                                    "latitude": lat,
                                    "longitude": lon
                                }
                            })
                            seen_nodes.add(loc_node_id)
                            
                        edge_key_loc = (crime_node_id, loc_node_id, "OCCURRED_AT")
                        if edge_key_loc not in seen_edges:
                            edges.append({
                                "source": crime_node_id,
                                "target": loc_node_id,
                                "relationship": "OCCURRED_AT"
                            })
                            seen_edges.add(edge_key_loc)
                            
            return {
                "nodes": nodes,
                "edges": edges,
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        else:
            criminal = self.repo.get_criminal_network(criminal_id, dataset_id=active_id)
            if not criminal:
                return None

            nodes = []
            edges = []
            seen_nodes = set()
            seen_edges = set()

            # Add criminal node
            c_node = self._serialize_criminal(criminal)
            nodes.append(c_node)
            seen_nodes.add(c_node["id"])

            for participation in criminal.participations:
                crime = participation.crime_event
                if crime and crime.dataset_id == active_id:
                    crime_id_str = f"crime_{crime.id}"
                    if crime_id_str not in seen_nodes:
                        cr_node = self._serialize_crime(crime)
                        nodes.append(cr_node)
                        seen_nodes.add(crime_id_str)

                    # Add INVOLVED_IN edge
                    edge_key = (c_node["id"], crime_id_str, "INVOLVED_IN")
                    if edge_key not in seen_edges:
                        edges.append({
                            "source": c_node["id"],
                            "target": crime_id_str,
                            "relationship": "INVOLVED_IN"
                        })
                        seen_edges.add(edge_key)

                    location = crime.location
                    if location:
                        loc_id_str = f"location_{location.id}"
                        if loc_id_str not in seen_nodes:
                            l_node = self._serialize_location(location)
                            nodes.append(l_node)
                            seen_nodes.add(loc_id_str)

                        # Add OCCURRED_AT edge
                        edge_key_loc = (crime_id_str, loc_id_str, "OCCURRED_AT")
                        if edge_key_loc not in seen_edges:
                            edges.append({
                                "source": crime_id_str,
                                "target": loc_id_str,
                                "relationship": "OCCURRED_AT"
                            })
                            seen_edges.add(edge_key_loc)

            return {
                "nodes": nodes,
                "edges": edges,
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }

    def build_crime_network(self, crime_id: int) -> Optional[Dict[str, Any]]:
        active_id = self._get_active_id()
        schema_type = self._get_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_people import Accused
            from backend.models.fir_geography import District, Unit
            
            case = self.db.query(CaseMaster).filter(CaseMaster.id == crime_id).first()
            if not case:
                return None
                
            nodes = []
            edges = []
            seen_nodes = set()
            seen_edges = set()
            
            crime_node_id = f"crime_{case.id}"
            nodes.append({
                "id": crime_node_id,
                "type": "crime",
                "label": case.crime_minor_head.CrimeHeadName if case.crime_minor_head else "Crime",
                "metadata": {
                    "crime_category": case.crime_major_head.CrimeGroupName if case.crime_major_head else "General",
                    "crime_subcategory": case.crime_minor_head.CrimeHeadName if case.crime_minor_head else "General",
                    "severity": 5.0 if case.gravity_offence.name == "Heinous" else 2.0,
                    "status": case.case_status.name if case.case_status else "Under Investigation",
                    "crime_date": str(case.registered_date) if case.registered_date else None,
                    "crime_time": None
                }
            })
            seen_nodes.add(crime_node_id)
            
            # Add occurrence District (Location)
            unit = self.db.query(Unit).filter(Unit.id == case.PoliceStationID).first()
            if unit and unit.DistrictID:
                district = self.db.query(District).filter(District.id == unit.DistrictID).first()
                if district:
                    loc_node_id = f"location_{district.id}"
                    if loc_node_id not in seen_nodes:
                        nodes.append({
                            "id": loc_node_id,
                            "type": "location",
                            "label": f"{district.name}, Karnataka",
                            "metadata": {
                                "state": "Karnataka",
                                "district": district.name,
                                "latitude": 12.9716,
                                "longitude": 77.5946
                            }
                        })
                        seen_nodes.add(loc_node_id)
                        
                    edge_key_loc = (crime_node_id, loc_node_id, "OCCURRED_AT")
                    if edge_key_loc not in seen_edges:
                        edges.append({
                            "source": crime_node_id,
                            "target": loc_node_id,
                            "relationship": "OCCURRED_AT"
                        })
                        seen_edges.add(edge_key_loc)
                        
            # Query accused linked to case
            accused_list = self.db.query(Accused).filter(Accused.CaseMasterID == case.id).all()
            for acc in accused_list:
                c_node_id = f"criminal_{acc.id}"
                if c_node_id not in seen_nodes:
                    nodes.append({
                        "id": c_node_id,
                        "type": "criminal",
                        "label": acc.AccusedName,
                        "metadata": {
                            "gender": acc.gender.name if acc.gender else "Male",
                            "age": acc.AgeYear,
                            "occupation": "Unknown",
                            "caste": "Unknown",
                            "risk_score": 5.0,
                            "status": "active"
                        }
                    })
                    seen_nodes.add(c_node_id)
                    
                edge_key = (c_node_id, crime_node_id, "INVOLVED_IN")
                if edge_key not in seen_edges:
                    edges.append({
                        "source": c_node_id,
                        "target": crime_node_id,
                        "relationship": "INVOLVED_IN"
                    })
                    seen_edges.add(edge_key)
                    
            return {
                "nodes": nodes,
                "edges": edges,
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        else:
            crime = self.repo.get_crime_network(crime_id, dataset_id=active_id)
            if not crime:
                return None

            nodes = []
            edges = []
            seen_nodes = set()
            seen_edges = set()

            # Add crime node
            cr_node = self._serialize_crime(crime)
            nodes.append(cr_node)
            seen_nodes.add(cr_node["id"])

            # Add location if present
            location = crime.location
            if location:
                loc_id_str = f"location_{location.id}"
                if loc_id_str not in seen_nodes:
                    l_node = self._serialize_location(location)
                    nodes.append(l_node)
                    seen_nodes.add(loc_id_str)

                # Add OCCURRED_AT edge
                edge_key_loc = (cr_node["id"], loc_id_str, "OCCURRED_AT")
                if edge_key_loc not in seen_edges:
                    edges.append({
                        "source": cr_node["id"],
                        "target": loc_id_str,
                        "relationship": "OCCURRED_AT"
                    })
                    seen_edges.add(edge_key_loc)

            for participation in crime.participations:
                criminal = participation.criminal
                if criminal and criminal.dataset_id == active_id:
                    criminal_id_str = f"criminal_{criminal.id}"
                    if criminal_id_str not in seen_nodes:
                        c_node = self._serialize_criminal(criminal)
                        nodes.append(c_node)
                        seen_nodes.add(criminal_id_str)

                    # Add INVOLVED_IN edge
                    edge_key = (criminal_id_str, cr_node["id"], "INVOLVED_IN")
                    if edge_key not in seen_edges:
                        edges.append({
                            "source": criminal_id_str,
                            "target": cr_node["id"],
                            "relationship": "INVOLVED_IN"
                        })
                        seen_edges.add(edge_key)

            return {
                "nodes": nodes,
                "edges": edges,
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }

    def build_location_network(self, location_id: int) -> Optional[Dict[str, Any]]:
        active_id = self._get_active_id()
        schema_type = self._get_schema_type()

        if schema_type == "fir_normalized":
            from backend.models.fir_case import CaseMaster
            from backend.models.fir_geography import District, Unit
            from backend.models.fir_people import Accused

            district = self.db.query(District).filter(District.id == location_id).first()
            if not district:
                return None
                
            nodes = []
            edges = []
            seen_nodes = set()
            seen_edges = set()
            
            loc_node_id = f"location_{district.id}"
            nodes.append({
                "id": loc_node_id,
                "type": "location",
                "label": f"{district.name}, Karnataka",
                "metadata": {
                    "state": "Karnataka",
                    "district": district.name,
                    "latitude": 12.9716,
                    "longitude": 77.5946
                }
            })
            seen_nodes.add(loc_node_id)
            
            # Load cases in this district
            cases = self.db.query(CaseMaster).join(Unit).filter(
                Unit.DistrictID == district.id,
                CaseMaster.dataset_id == active_id
            ).all()
            
            for case in cases:
                crime_node_id = f"crime_{case.id}"
                if crime_node_id not in seen_nodes:
                    nodes.append({
                        "id": crime_node_id,
                        "type": "crime",
                        "label": case.crime_minor_head.CrimeHeadName if case.crime_minor_head else "Crime",
                        "metadata": {
                            "crime_category": case.crime_major_head.CrimeGroupName if case.crime_major_head else "General",
                            "crime_subcategory": case.crime_minor_head.CrimeHeadName if case.crime_minor_head else "General",
                            "severity": 5.0 if case.gravity_offence.name == "Heinous" else 2.0,
                            "status": case.case_status.name if case.case_status else "Under Investigation",
                            "crime_date": str(case.registered_date) if case.registered_date else None,
                            "crime_time": None
                        }
                    })
                    seen_nodes.add(crime_node_id)
                    
                edge_key_loc = (crime_node_id, loc_node_id, "OCCURRED_AT")
                if edge_key_loc not in seen_edges:
                    edges.append({
                        "source": crime_node_id,
                        "target": loc_node_id,
                        "relationship": "OCCURRED_AT"
                    })
                    seen_edges.add(edge_key_loc)
                    
                # Accused in these cases
                accused_list = self.db.query(Accused).filter(Accused.CaseMasterID == case.id).all()
                for acc in accused_list:
                    c_node_id = f"criminal_{acc.id}"
                    if c_node_id not in seen_nodes:
                        nodes.append({
                            "id": c_node_id,
                            "type": "criminal",
                            "label": acc.AccusedName,
                            "metadata": {
                                "gender": acc.gender.name if acc.gender else "Male",
                                "age": acc.AgeYear,
                                "occupation": "Unknown",
                                "caste": "Unknown",
                                "risk_score": 5.0,
                                "status": "active"
                            }
                        })
                        seen_nodes.add(c_node_id)
                        
                    edge_key = (c_node_id, crime_node_id, "INVOLVED_IN")
                    if edge_key not in seen_edges:
                        edges.append({
                            "source": c_node_id,
                            "target": crime_node_id,
                            "relationship": "INVOLVED_IN"
                        })
                        seen_edges.add(edge_key)
                        
            return {
                "nodes": nodes,
                "edges": edges,
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        else:
            location = self.repo.get_location_network(location_id, dataset_id=active_id)
            if not location:
                return None

            nodes = []
            edges = []
            seen_nodes = set()
            seen_edges = set()

            # Add location node
            l_node = self._serialize_location(location)
            nodes.append(l_node)
            seen_nodes.add(l_node["id"])

            for crime in location.crime_events:
                if crime.dataset_id != active_id:
                    continue
                crime_id_str = f"crime_{crime.id}"
                if crime_id_str not in seen_nodes:
                    cr_node = self._serialize_crime(crime)
                    nodes.append(cr_node)
                    seen_nodes.add(crime_id_str)

                # Add OCCURRED_AT edge
                edge_key_loc = (crime_id_str, l_node["id"], "OCCURRED_AT")
                if edge_key_loc not in seen_edges:
                    edges.append({
                        "source": crime_id_str,
                        "target": l_node["id"],
                        "relationship": "OCCURRED_AT"
                    })
                    seen_edges.add(edge_key_loc)

                for participation in crime.participations:
                    criminal = participation.criminal
                    if criminal and criminal.dataset_id == active_id:
                        criminal_id_str = f"criminal_{criminal.id}"
                        if criminal_id_str not in seen_nodes:
                            c_node = self._serialize_criminal(criminal)
                            nodes.append(c_node)
                            seen_nodes.add(criminal_id_str)

                        # Add INVOLVED_IN edge
                        edge_key = (criminal_id_str, crime_id_str, "INVOLVED_IN")
                        if edge_key not in seen_edges:
                            edges.append({
                                "source": criminal_id_str,
                                "target": crime_id_str,
                                "relationship": "INVOLVED_IN"
                            })
                            seen_edges.add(edge_key)

            return {
                "nodes": nodes,
                "edges": edges,
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }

    # Stubs kept for backward compatibility
    def build_network_graph(self) -> Dict[str, Any]:
        return {"nodes": [], "edges": []}

    def compute_centrality_indexes(self) -> Dict[str, Any]:
        return {}
