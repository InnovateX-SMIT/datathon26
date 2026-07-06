from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List, Set
from backend.repositories.network_repository import NetworkRepository

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

    def build_criminal_network(self, criminal_id: int) -> Optional[Dict[str, Any]]:
        active_id = self._get_active_id()
        criminal = self.repo.get_criminal_network(criminal_id, dataset_id=active_id)
        if not criminal:
            return None

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []
        seen_nodes: Set[str] = set()
        seen_edges: Set[tuple] = set()

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
        crime = self.repo.get_crime_network(crime_id, dataset_id=active_id)
        if not crime:
            return None

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []
        seen_nodes: Set[str] = set()
        seen_edges: Set[tuple] = set()

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

                # Add INVOLVED_IN edge (Criminal -> Crime)
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
        location = self.repo.get_location_network(location_id, dataset_id=active_id)
        if not location:
            return None

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []
        seen_nodes: Set[str] = set()
        seen_edges: Set[tuple] = set()

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

            # Add OCCURRED_AT edge (Crime -> Location)
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

                    # Add INVOLVED_IN edge (Criminal -> Crime)
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

