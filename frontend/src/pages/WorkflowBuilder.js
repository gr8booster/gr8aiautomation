import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Sparkles, Play, Save } from 'lucide-react';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';
import { apiCall } from '../utils/api';

const initialNodes = [
  {
    id: '1',
    type: 'input',
    data: { label: '🎯 Trigger: Form Submission' },
    position: { x: 250, y: 5 },
    style: { background: '#0c969b', color: 'white', border: '2px solid #0a7a7e', borderRadius: '8px', padding: '10px' }
  }
];

const nodeTypes = [
  { type: 'trigger', label: 'Form Submission', icon: '📝', color: '#0c969b' },
  { type: 'trigger', label: 'Webhook', icon: '🔗', color: '#0c969b' },
  { type: 'action', label: 'Send Email', icon: '📧', color: '#3b82f6' },
  { type: 'action', label: 'AI Response', icon: '🤖', color: '#3b82f6' },
  { type: 'condition', label: 'If/Else', icon: '🔀', color: '#f59e0b' }
];

export default function WorkflowBuilder() {
  const navigate = useNavigate();
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [workflowName, setWorkflowName] = useState('New Workflow');

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge({
      ...params,
      markerEnd: { type: MarkerType.ArrowClosed },
      style: { strokeWidth: 2, stroke: '#0c969b' }
    }, eds)),
    []
  );

  const addNode = (nodeType) => {
    const newNode = {
      id: `${nodes.length + 1}`,
      data: { label: `${nodeType.icon} ${nodeType.label}` },
      position: { x: Math.random() * 400 + 100, y: Math.random() * 400 + 100 },
      style: { background: nodeType.color, color: 'white', border: `2px solid ${nodeType.color}`, borderRadius: '8px', padding: '10px' }
    };
    setNodes((nds) => nds.concat(newNode));
    toast.success(`Added ${nodeType.label}`);
  };

  const saveWorkflow = async () => {
    try {
      await apiCall('/api/workflows/save', {
        method: 'POST',
        body: JSON.stringify({ name: workflowName, nodes, edges })
      });
      toast.success('Workflow saved!');
    } catch (error) {
      toast.error('Failed to save');
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      <header className="border-b border-border bg-card/50 backdrop-blur-sm z-50">
        <div className="mx-auto max-w-full px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Sparkles className="h-6 w-6 text-primary" />
              <input
                type="text"
                value={workflowName}
                onChange={(e) => setWorkflowName(e.target.value)}
                className="px-3 py-1 border border-border rounded-md bg-background font-semibold"
              />
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={saveWorkflow}>
                <Save className="h-4 w-4 mr-2" /> Save
              </Button>
              <Button onClick={() => toast.info('Execution coming soon!')}>
                <Play className="h-4 w-4 mr-2" /> Run
              </Button>
              <Button variant="ghost" onClick={() => navigate('/dashboard')}>Dashboard</Button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex">
        <div className="w-64 border-r border-border bg-card p-4 overflow-y-auto">
          <h3 className="font-semibold mb-4">Add Nodes</h3>
          <div className="space-y-2">
            {nodeTypes.map((node, idx) => (
              <button
                key={idx}
                onClick={() => addNode(node)}
                className="w-full text-left p-3 rounded-lg border border-border hover:border-primary hover:bg-primary/5 transition-colors"
              >
                <span className="text-xl mr-2">{node.icon}</span>
                <span className="font-medium text-sm">{node.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            fitView
          >
            <Controls />
            <MiniMap />
            <Background variant="dots" gap={12} size={1} />
          </ReactFlow>
        </div>
      </div>
    </div>
  );
}
