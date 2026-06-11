import { useState, useCallback } from "react";
import { useNodesState, useEdgesState, Node, Edge } from "@xyflow/react";
import axios from "axios";
import { fetchNetworkGraph } from "@/services/network.service";
import { transformGraphResponse } from "@/features/network/utils/graphTransform";

export interface NetworkStatistics {
  totalNodes: number;
  totalEdges: number;
  criminalNodes: number;
  crimeNodes: number;
  locationNodes: number;
}

export function useNetworkGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [statistics, setStatistics] = useState<NetworkStatistics>({
    totalNodes: 0,
    totalEdges: 0,
    criminalNodes: 0,
    crimeNodes: 0,
    locationNodes: 0,
  });

  const loadNetwork = useCallback(async (criminalId: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchNetworkGraph(criminalId);
      
      if (!response || !response.nodes) {
        throw new Error("No network graph data returned");
      }

      // Convert backend nodes and edges to React Flow format
      const transformed = transformGraphResponse(response);
      
      setNodes(transformed.nodes);
      setEdges(transformed.edges);

      // Extract statistics from the raw API response (avoid calculating centrality or complex metrics)
      const rawNodes = response.nodes || [];
      const stats: NetworkStatistics = {
        totalNodes: response.total_nodes || rawNodes.length,
        totalEdges: response.total_edges || (response.edges || []).length,
        criminalNodes: rawNodes.filter((n) => n.type === "criminal").length,
        crimeNodes: rawNodes.filter((n) => n.type === "crime" || n.type === "event").length,
        locationNodes: rawNodes.filter((n) => n.type === "location").length,
      };
      
      setStatistics(stats);
    } catch (err) {
      console.error("Error loading criminal network graph:", err);
      // Clean up graph on error
      setNodes([]);
      setEdges([]);
      setStatistics({
        totalNodes: 0,
        totalEdges: 0,
        criminalNodes: 0,
        crimeNodes: 0,
        locationNodes: 0,
      });

      // Present clean user-friendly messages
      if (axios.isAxiosError(err) && err.response?.status === 404) {
        setError(`Criminal network for ID ${criminalId} not found.`);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load network data. Check backend connection.");
      }
    } finally {
      setLoading(false);
    }
  }, [setNodes, setEdges]);

  return {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    loading,
    error,
    loadNetwork,
    statistics,
  };
}
