import type { NetworkGraphResponse } from "@/types/network";

interface ReactFlowPosition {
  x: number;
  y: number;
}

interface ReactFlowNode {
  id: string;
  type: string;
  data: {
    label: string;
    type: string;
    metadata: Record<string, unknown>;
  };
  position: ReactFlowPosition;
}

interface ReactFlowEdge {
  id: string;
  source: string;
  target: string;
  animated: boolean;
  label?: string;
  type: string;
  style?: Record<string, string | number>;
}

export function transformGraphResponse(response: NetworkGraphResponse) {
  const { nodes = [], edges = [] } = response;

  // Group nodes by type
  const criminals = nodes.filter((n) => n.type === "criminal");
  const crimes = nodes.filter((n) => n.type === "crime" || n.type === "event");
  const locations = nodes.filter((n) => n.type === "location");

  const reactFlowNodes: ReactFlowNode[] = [];

  // Spacing parameters
  const xSpacing = 280;
  const centerY = 300;
  const centerX = 400;

  // 1. Position criminals on top (y = 80)
  const crimCount = criminals.length;
  const crimStartX = centerX - ((crimCount - 1) * xSpacing) / 2;
  criminals.forEach((node, index) => {
    reactFlowNodes.push({
      id: node.id,
      type: "criminal",
      data: {
        label: node.label,
        type: node.type,
        metadata: node.metadata,
      },
      position: {
        x: crimCount > 1 ? crimStartX + index * xSpacing : centerX,
        y: 80,
      },
    });
  });

  // 2. Position crime events in middle (y = 280)
  const crimeCount = crimes.length;
  const crimeStartX = centerX - ((crimeCount - 1) * xSpacing) / 2;
  crimes.forEach((node, index) => {
    reactFlowNodes.push({
      id: node.id,
      type: "crime",
      data: {
        label: node.label,
        type: node.type,
        metadata: node.metadata,
      },
      position: {
        x: crimeCount > 1 ? crimeStartX + index * xSpacing : centerX,
        y: 280,
      },
    });
  });

  // 3. Position locations at bottom (y = 480)
  const locCount = locations.length;
  const locStartX = centerX - ((locCount - 1) * xSpacing) / 2;
  locations.forEach((node, index) => {
    reactFlowNodes.push({
      id: node.id,
      type: "location",
      data: {
        label: node.label,
        type: node.type,
        metadata: node.metadata,
      },
      position: {
        x: locCount > 1 ? locStartX + index * xSpacing : centerX,
        y: 480,
      },
    });
  });

  // Handle any other node type that doesn't fit the three categories
  const otherNodes = nodes.filter(
    (n) => n.type !== "criminal" && n.type !== "crime" && n.type !== "event" && n.type !== "location"
  );
  otherNodes.forEach((node, index) => {
    reactFlowNodes.push({
      id: node.id,
      type: "default",
      data: {
        label: node.label,
        type: node.type,
        metadata: node.metadata,
      },
      position: {
        x: centerX + index * 50,
        y: centerY + 300,
      },
    });
  });

  // Map edges to React Flow format
  const reactFlowEdges: ReactFlowEdge[] = edges.map((edge, index) => {
    const isCriminalToCrime = edge.source.startsWith("criminal_") || edge.target.startsWith("crime_");
    
    // Choose custom styles
    const edgeColor = isCriminalToCrime ? "#6366f1" : "#10b981"; // Indigo for criminal links, Emerald for location links

    return {
      id: `edge_${index}_${edge.source}_${edge.target}`,
      source: edge.source,
      target: edge.target,
      animated: isCriminalToCrime, // Animate links between criminals and crimes for high fidelity
      label: edge.relationship,
      type: "smoothstep",
      style: {
        stroke: edgeColor,
        strokeWidth: 2,
      },
    };
  });

  return {
    nodes: reactFlowNodes,
    edges: reactFlowEdges,
  };
}
