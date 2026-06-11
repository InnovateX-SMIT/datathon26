import React, { useEffect } from "react";
import {
  ReactFlow,
  Background,
  MiniMap,
  useReactFlow,
  ReactFlowProvider,
  Node,
  Edge,
  OnNodesChange,
  OnEdgesChange,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import CriminalNode from "./CriminalNode";
import CrimeEventNode from "./CrimeEventNode";
import LocationNode from "./LocationNode";
import NetworkControls from "./NetworkControls";

// Register custom node types outside the component to prevent re-renders
const nodeTypes = {
  criminal: CriminalNode,
  crime: CrimeEventNode,
  location: LocationNode,
};

interface CriminalNetworkGraphContentProps {
  nodes: Node[];
  edges: Edge[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
}

function CriminalNetworkGraphContent({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
}: CriminalNetworkGraphContentProps) {
  const { fitView } = useReactFlow();

  // Fit view whenever nodes change (e.g. when a new graph is loaded)
  useEffect(() => {
    if (nodes.length > 0) {
      const timer = setTimeout(() => {
        fitView({ padding: 0.15, duration: 800 });
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [nodes, fitView]);

  const miniMapNodeColor = (node: Node) => {
    switch (node.type) {
      case "criminal":
        return "#3b82f6"; // Blue
      case "crime":
        return "#f59e0b"; // Orange
      case "location":
        return "#10b981"; // Green
      default:
        return "#64748b"; // Gray
    }
  };

  return (
    <div className="w-full h-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.2}
        maxZoom={2}
        className="w-full h-full"
      >
        <Background color="#1e293b" gap={16} size={1} />
        
        {/* Custom floating controls */}
        <NetworkControls />
        
        <MiniMap
          nodeColor={miniMapNodeColor}
          maskColor="rgba(7, 11, 19, 0.7)"
          bgColor="#020617"
          className="!bg-slate-950/90 !border !border-slate-800 !rounded-xl !bottom-4 !right-4 !shadow-xl backdrop-blur-sm"
        />
      </ReactFlow>
    </div>
  );
}

interface CriminalNetworkGraphProps {
  nodes: Node[];
  edges: Edge[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
}

export default function CriminalNetworkGraph(props: CriminalNetworkGraphProps) {
  return (
    <div className="w-full h-[600px] border border-slate-900 bg-slate-950/40 rounded-3xl overflow-hidden relative shadow-inner">
      <ReactFlowProvider>
        <CriminalNetworkGraphContent {...props} />
      </ReactFlowProvider>
    </div>
  );
}
