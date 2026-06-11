import networkx as nx
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from backend.repositories.network_repository import NetworkRepository

class NetworkAnalyticsService:
    # Class-level cache for graph to avoid rebuilding on every API request
    _cached_graph: Optional[nx.Graph] = None

    def __init__(self, db: Session):
        self.db = db
        self.repo = NetworkRepository(db)

    def get_graph(self, force_rebuild: bool = False) -> nx.Graph:
        """
        Retrieves the cached network graph. If the cache is empty or in-memory testing
        database is active, rebuilds the graph dynamically to guarantee test isolation.
        """
        # Test database checks
        is_test = False
        try:
            bind = self.db.bind
            if bind and hasattr(bind, "url") and bind.url:
                is_test = bind.url.drivername == "sqlite" and (bind.url.database == ":memory:" or not bind.url.database)
        except Exception:
            pass

        if NetworkAnalyticsService._cached_graph is None or force_rebuild or is_test:
            NetworkAnalyticsService._cached_graph = self.build_graph()
        return NetworkAnalyticsService._cached_graph

    def build_graph(self) -> nx.Graph:
        """
        Queries bulk records from the repository and constructs an undirected NetworkX Graph.
        """
        G = nx.Graph()

        # 1. Load entities
        criminals = self.repo.get_all_criminals()
        crimes = self.repo.get_all_crimes()
        locations = self.repo.get_all_locations()
        participations = self.repo.get_all_participations()

        # 2. Add criminal nodes
        for c in criminals:
            G.add_node(
                f"criminal_{c.id}",
                type="criminal",
                label=c.name,
                risk_score=c.risk_score or 0.0,
                gender=c.gender,
                age=c.age,
                occupation=c.occupation,
                caste=c.caste,
                status=c.status
            )

        # 3. Add crime event nodes
        for cr in crimes:
            G.add_node(
                f"crime_{cr.id}",
                type="crime",
                label=cr.crime_type,
                crime_category=cr.crime_category,
                crime_subcategory=cr.crime_subcategory,
                severity=cr.severity or 1.0,
                status=cr.status,
                crime_date=str(cr.crime_date) if cr.crime_date else None
            )

        # 4. Add location nodes
        for loc in locations:
            G.add_node(
                f"location_{loc.id}",
                type="location",
                label=f"{loc.district}, {loc.state}",
                district=loc.district,
                state=loc.state,
                latitude=loc.latitude,
                longitude=loc.longitude
            )

        # 5. Add edges for Crime Participation: Criminal -> Crime Event
        for part in participations:
            crim_node_id = f"criminal_{part.criminal_id}"
            crime_node_id = f"crime_{part.crime_event_id}"
            
            # Verify nodes exist before linking to prevent isolated/broken edges
            if G.has_node(crim_node_id) and G.has_node(crime_node_id):
                G.add_edge(
                    crim_node_id,
                    crime_node_id,
                    relationship="INVOLVED_IN",
                    role=part.role or "accused"
                )

        # 6. Add edges for Crime Occurrence: Crime Event -> Location
        for cr in crimes:
            if cr.location_id:
                crime_node_id = f"crime_{cr.id}"
                loc_node_id = f"location_{cr.location_id}"
                
                if G.has_node(crime_node_id) and G.has_node(loc_node_id):
                    G.add_edge(
                        crime_node_id,
                        loc_node_id,
                        relationship="OCCURRED_AT"
                    )

        return G

    def get_centrality(self, limit: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """
        Computes Degree, Betweenness (k-sampled), and Closeness Centrality scores,
        ranking the top N nodes.
        """
        G = self.get_graph()
        if len(G) == 0:
            return {"degree": [], "betweenness": [], "closeness": []}

        # Calculate centralities
        deg_cent = nx.degree_centrality(G)
        
        # Optimize betweenness for scalability using k-sampling
        k_val = min(len(G), 100)
        bet_cent = nx.betweenness_centrality(G, k=k_val)
        
        cloc_cent = nx.closeness_centrality(G)

        def rank_and_format(cent_dict) -> List[Dict[str, Any]]:
            sorted_nodes = sorted(cent_dict.items(), key=lambda x: x[1], reverse=True)[:limit]
            formatted = []
            for node_id, score in sorted_nodes:
                node_data = G.nodes[node_id]
                formatted.append({
                    "id": node_id,
                    "type": node_data.get("type", "unknown"),
                    "label": node_data.get("label", "Unknown"),
                    "score": float(score)
                })
            return formatted

        return {
            "degree": rank_and_format(deg_cent),
            "betweenness": rank_and_format(bet_cent),
            "closeness": rank_and_format(cloc_cent)
        }

    def get_clusters(self) -> List[Dict[str, Any]]:
        """
        Finds connected sub-components (gangs / crime groups) sorting by size.
        """
        G = self.get_graph()
        if len(G) == 0:
            return []

        components = sorted(nx.connected_components(G), key=len, reverse=True)
        
        clusters = []
        for i, comp in enumerate(components):
            members = []
            criminal_count = 0
            crime_count = 0
            location_count = 0
            
            for node_id in comp:
                node_data = G.nodes[node_id]
                ntype = node_data.get("type", "unknown")
                if ntype == "criminal":
                    criminal_count += 1
                elif ntype == "crime":
                    crime_count += 1
                elif ntype == "location":
                    location_count += 1
                
                members.append({
                    "id": node_id,
                    "type": ntype,
                    "label": node_data.get("label", "Unknown")
                })
            
            clusters.append({
                "cluster_id": f"cluster_{i+1}",
                "members": members,
                "size": len(comp),
                "criminal_count": criminal_count,
                "crime_count": crime_count,
                "location_count": location_count
            })
            
        return clusters

    def get_repeat_associations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Discovers co-offending pairs of criminals appearing together on the same crime events,
        determining Jaccard-based association strength and co-occurrence frequency.
        """
        from collections import defaultdict
        import itertools

        G = self.get_graph()
        crimes = [n for n, attr in G.nodes(data=True) if attr.get("type") == "crime"]
        
        pair_shared_crimes = defaultdict(list)
        for crime_id in crimes:
            # Gather all participating criminals
            crims = [nbr for nbr in G.neighbors(crime_id) if G.nodes[nbr].get("type") == "criminal"]
            if len(crims) >= 2:
                for crim_a, crim_b in itertools.combinations(sorted(crims), 2):
                    pair_shared_crimes[(crim_a, crim_b)].append(crime_id)

        associations = []
        for (crim_a, crim_b), shared_list in pair_shared_crimes.items():
            deg_a = G.degree(crim_a)
            deg_b = G.degree(crim_b)
            freq = len(shared_list)
            
            # Compute normalized co-offending Jaccard score
            strength = freq / (deg_a + deg_b - freq) if (deg_a + deg_b - freq) > 0 else 0.0
            
            node_a_data = G.nodes[crim_a]
            node_b_data = G.nodes[crim_b]
            
            shared_crime_details = []
            for c_id in shared_list:
                c_data = G.nodes[c_id]
                shared_crime_details.append({
                    "id": c_id,
                    "type": "crime",
                    "label": c_data.get("label", "Unknown"),
                    "metadata": {
                        "crime_category": c_data.get("crime_category"),
                        "severity": c_data.get("severity")
                    }
                })
            
            associations.append({
                "criminal_a": {
                    "id": crim_a,
                    "type": "criminal",
                    "label": node_a_data.get("label", "Unknown"),
                    "metadata": {"risk_score": node_a_data.get("risk_score")}
                },
                "criminal_b": {
                    "id": crim_b,
                    "type": "criminal",
                    "label": node_b_data.get("label", "Unknown"),
                    "metadata": {"risk_score": node_b_data.get("risk_score")}
                },
                "shared_crimes": shared_crime_details,
                "frequency": freq,
                "strength": float(strength)
            })
            
        # Sort co-offenders by count of shared crimes, then Jaccard index
        associations.sort(key=lambda x: (-x["frequency"], -x["strength"]))
        return associations[:limit]

    def get_location_intelligence(self, limit: int = 50) -> Dict[str, Any]:
        """
        Generates location rankings by crime event activity, criminal diversity connections,
        and linked spatial networks via criminal crossovers.
        """
        from collections import defaultdict
        import itertools

        G = self.get_graph()
        locations = [n for n, attr in G.nodes(data=True) if attr.get("type") == "location"]
        
        loc_details = []
        for loc_id in locations:
            attr = G.nodes[loc_id]
            connected_crimes = list(G.neighbors(loc_id))
            
            distinct_criminals = set()
            for crime_id in connected_crimes:
                criminals = [nbr for nbr in G.neighbors(crime_id) if G.nodes[nbr].get("type") == "criminal"]
                distinct_criminals.update(criminals)
                
            loc_details.append({
                "id": loc_id,
                "district": attr.get("district", "Unknown"),
                "state": attr.get("state", "Unknown"),
                "degree": len(connected_crimes),
                "crime_count": len(connected_crimes),
                "criminal_count": len(distinct_criminals)
            })
            
        most_active = sorted(loc_details, key=lambda x: x["crime_count"], reverse=True)[:limit]
        most_connected = sorted(loc_details, key=lambda x: x["criminal_count"], reverse=True)[:limit]

        # Location crossovers (Locations linked by criminals committing offences in both)
        loc_pairs = defaultdict(set)
        criminals = [n for n, attr in G.nodes(data=True) if attr.get("type") == "criminal"]
        
        for crim_id in criminals:
            crim_crimes = list(G.neighbors(crim_id))
            crim_locs = set()
            for crime_id in crim_crimes:
                locs = [nbr for nbr in G.neighbors(crime_id) if G.nodes[nbr].get("type") == "location"]
                crim_locs.update(locs)
            
            if len(crim_locs) >= 2:
                for loc_a, loc_b in itertools.combinations(sorted(list(crim_locs)), 2):
                    loc_pairs[(loc_a, loc_b)].add(crim_id)
                    
        location_links = []
        for (loc_a, loc_b), crim_set in loc_pairs.items():
            loc_a_attr = G.nodes[loc_a]
            loc_b_attr = G.nodes[loc_b]
            
            connecting_details = []
            for c_id in crim_set:
                connecting_details.append({
                    "id": c_id,
                    "type": "criminal",
                    "label": G.nodes[c_id].get("label", "Unknown")
                })
                
            location_links.append({
                "location_a": {
                    "id": loc_a,
                    "type": "location",
                    "label": loc_a_attr.get("label", "Unknown")
                },
                "location_b": {
                    "id": loc_b,
                    "type": "location",
                    "label": loc_b_attr.get("label", "Unknown")
                },
                "connecting_criminals": connecting_details,
                "strength": len(crim_set)
            })
            
        location_links.sort(key=lambda x: x["strength"], reverse=True)
        
        return {
            "most_active": most_active,
            "most_connected": most_connected,
            "location_links": location_links[:limit]
        }

    def find_shortest_path(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """
        Computes the shortest path relationship route between any two network nodes.
        """
        G = self.get_graph()
        
        if source_id not in G or target_id not in G:
            return {
                "path_found": False,
                "nodes": [],
                "edges": [],
                "path_length": 0
            }
            
        try:
            path = nx.shortest_path(G, source=source_id, target=target_id)
            
            path_nodes = []
            for n_id in path:
                node_attr = G.nodes[n_id]
                path_nodes.append({
                    "id": n_id,
                    "type": node_attr.get("type", "unknown"),
                    "label": node_attr.get("label", "Unknown")
                })
                
            path_edges = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                edge_data = G.get_edge_data(u, v)
                path_edges.append({
                    "source": u,
                    "target": v,
                    "relationship": edge_data.get("relationship", "CONNECTED_TO")
                })
                
            return {
                "path_found": True,
                "nodes": path_nodes,
                "edges": path_edges,
                "path_length": len(path_edges)
            }
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return {
                "path_found": False,
                "nodes": [],
                "edges": [],
                "path_length": 0
            }
