from typing import Dict, Any, List
import asyncio
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

from .base import BaseAgent, AgentResult
from ..core.state import state_manager
from .ingestion_agent import DataIngestionAgent
from .question_agent import QuestionGenerationAgent
from .faq_agent import FAQGenerationAgent
from .product_page_agent import ProductPageAgent
from .product_b_agent import ProductBCreationAgent
from .comparison_agent import ComparisonPageAgent
from .output_agent import OutputGenerationAgent


class OrchestratorAgent(BaseAgent):
    """Orchestrates the entire agent pipeline with DAG execution"""
    
    def __init__(self):
        super().__init__("orchestrator_v1", "Pipeline Orchestrator")
        self.agents = {}
        self.dag = nx.DiGraph()
        self._build_dag()
    
    def _build_dag(self):
        """Build the CORRECT execution DAG with proper dependencies"""
        # Define agent nodes
        agents = [
            ("data_ingestion", DataIngestionAgent()),
            ("question_generation", QuestionGenerationAgent()),
            ("faq_generation", FAQGenerationAgent()),
            ("product_page", ProductPageAgent()),
            ("product_b_creation", ProductBCreationAgent()),
            ("comparison_page", ComparisonPageAgent()),
            ("output_generation", OutputGenerationAgent())
        ]
        
        # Add nodes
        for agent_id, agent in agents:
            self.agents[agent_id] = agent
            self.dag.add_node(agent_id, agent=agent)
        
        # CORRECTED DEPENDENCIES:
        # 1. data_ingestion is the root - everyone depends on it
        root_dependencies = [
            ("data_ingestion", "question_generation"),
            ("data_ingestion", "product_page"),
            ("data_ingestion", "product_b_creation"),
        ]
        
        # 2. question_generation -> faq_generation
        faq_dependencies = [
            ("question_generation", "faq_generation"),
        ]
        
        # 3. product_b_creation -> comparison_page
        comparison_dependencies = [
            ("product_b_creation", "comparison_page"),
            ("data_ingestion", "comparison_page"),  # Also need main product data
        ]
        
        # 4. All content agents -> output_generation
        output_dependencies = [
            ("faq_generation", "output_generation"),
            ("product_page", "output_generation"),
            ("comparison_page", "output_generation"),
        ]
        
        # Add all edges
        all_dependencies = (
            root_dependencies + 
            faq_dependencies + 
            comparison_dependencies + 
            output_dependencies
        )
        
        for from_agent, to_agent in all_dependencies:
            self.dag.add_edge(from_agent, to_agent)
        
        # Validate DAG
        if not nx.is_directed_acyclic_graph(self.dag):
            raise RuntimeError("Invalid DAG: Circular dependencies detected")
    
    async def _execute_impl(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the pipeline using topological sort"""
        raw_data = context.get("raw_product_data")
        if not raw_data:
            raise ValueError("raw_product_data required in context")
        
        # Initialize state
        state_manager.initialize_state(raw_data)
        
        # Get topological order
        try:
            execution_order = list(nx.topological_sort(self.dag))
        except nx.NetworkXUnfeasible:
            raise RuntimeError("Circular dependency detected in agent DAG")
        
        execution_results = {}
        
        # Execute agents in order
        for agent_id in execution_order:
            agent = self.dag.nodes[agent_id]["agent"]
            print(f"🚀 Executing: {agent.agent_name}")
            
            result = await agent.execute(context)
            
            if not result.success:
                raise RuntimeError(
                    f"Agent {agent.agent_name} failed: {result.error}"
                )
            
            execution_results[agent_id] = {
                "success": result.success,
                "execution_time_ms": result.execution_time_ms,
                "data_keys": list(result.data.keys()) if result.data else []
            }
            
            print(f"✅ Completed: {agent.agent_name} ({result.execution_time_ms:.0f}ms)")
        
        # Generate DAG visualization
        self._visualize_dag()
        
        # Get final state snapshot
        state_snapshot = state_manager.get_state_snapshot()
        
        return {
            "pipeline_success": True,
            "agents_executed": len(execution_results),
            "execution_order": execution_order,
            "agent_results": execution_results,
            "state_snapshot": state_snapshot,
            "output_files": ["faq.json", "product_page.json", "comparison_page.json"]
        }
    
    def _visualize_dag(self):
        """Generate DAG visualization with proper layout"""
        plt.figure(figsize=(14, 10))
        
        # Use hierarchical layout for better visualization
        pos = {}
        
        # Define positions for better visualization
        layers = {
            0: ["data_ingestion"],
            1: ["question_generation", "product_page", "product_b_creation"],
            2: ["faq_generation", "comparison_page"],
            3: ["output_generation"]
        }
        
        for layer, nodes in layers.items():
            x_positions = [i * 2 for i in range(len(nodes))]
            for i, node in enumerate(nodes):
                pos[node] = (x_positions[i], -layer * 2)
        
        # Draw nodes with colors based on role
        node_colors = []
        node_labels = {}
        for node in self.dag.nodes():
            agent = self.agents[node]
            
            # Color coding
            if node == "data_ingestion":
                node_colors.append("#4CAF50")  # Green - input
                node_labels[node] = "📥 Input\n" + agent.agent_name
            elif node == "output_generation":
                node_colors.append("#FF9800")  # Orange - output
                node_labels[node] = "💾 Output\n" + agent.agent_name
            elif "generation" in node or "creation" in node:
                node_colors.append("#2196F3")  # Blue - generation
                node_labels[node] = "🧠 " + agent.agent_name
            else:
                node_colors.append("#9C27B0")  # Purple - processing
                node_labels[node] = "⚙️ " + agent.agent_name
        
        nx.draw_networkx_nodes(self.dag, pos, 
                             node_color=node_colors, 
                             node_size=4000,
                             alpha=0.9,
                             edgecolors='black',
                             linewidths=2)
        
        # Draw edges with arrows
        nx.draw_networkx_edges(self.dag, pos, 
                              arrowstyle='->',
                              arrowsize=25,
                              edge_color='#666666',
                              width=2,
                              connectionstyle='arc3,rad=0.1')
        
        # Draw labels
        nx.draw_networkx_labels(self.dag, pos, 
                               node_labels, 
                               font_size=9,
                               font_weight='bold')
        
        # Add title and legend
        plt.title("Multi-Agent Content Generation Pipeline DAG", 
                 fontsize=16, fontweight='bold', pad=20)
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#4CAF50', markersize=10, 
                      label='Input Agent'),
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#2196F3', markersize=10, 
                      label='Generation Agent'),
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#9C27B0', markersize=10, 
                      label='Processing Agent'),
            plt.Line2D([0], [0], marker='o', color='w', 
                      markerfacecolor='#FF9800', markersize=10, 
                      label='Output Agent'),
        ]
        plt.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        plt.axis('off')
        
        # Add layer labels
        for layer in layers:
            plt.text(-1, -layer * 2, f"Layer {layer}", 
                    fontsize=10, fontweight='bold',
                    verticalalignment='center')
        
        # Save to docs directory
        output_dir = Path("docs/diagrams")
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_dir / "execution_dag.png", 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"\n📊 DAG visualization saved to {output_dir}/execution_dag.png")
    
    def get_execution_plan(self) -> Dict[str, Any]:
        """Get execution plan without running"""
        execution_order = list(nx.topological_sort(self.dag))
        
        # Group by execution layer
        layers = {}
        for agent_id in execution_order:
            # Calculate longest path to root for layer determination
            paths = nx.single_source_shortest_path_length(self.dag.reverse(), agent_id)
            layer = max(paths.values()) if paths else 0
            if layer not in layers:
                layers[layer] = []
            layers[layer].append({
                "id": agent_id,
                "name": self.agents[agent_id].agent_name
            })
        
        return {
            "total_agents": len(self.agents),
            "execution_order": execution_order,
            "execution_layers": layers,
            "dependencies": [
                {
                    "from": edge[0],
                    "to": edge[1],
                    "from_name": self.agents[edge[0]].agent_name,
                    "to_name": self.agents[edge[1]].agent_name,
                    "dependency_type": self._get_dependency_type(edge[0], edge[1])
                }
                for edge in self.dag.edges()
            ],
            "parallelizable_groups": self._find_parallel_groups()
        }
    
    def _get_dependency_type(self, from_agent: str, to_agent: str) -> str:
        """Determine type of dependency"""
        if from_agent == "data_ingestion":
            return "data_input"
        elif "generation" in from_agent and "generation" in to_agent:
            return "content_flow"
        elif "creation" in from_agent and "page" in to_agent:
            return "content_source"
        else:
            return "processing_chain"
    
    def _find_parallel_groups(self) -> List[List[str]]:
        """Find groups of agents that can run in parallel"""
        # Use topological sorting layers
        topological_order = list(nx.topological_sort(self.dag))
        
        # Create dependency graph
        incoming_deps = {}
        for node in self.dag.nodes():
            incoming_deps[node] = set(self.dag.predecessors(node))
        
        layers = []
        remaining = set(self.dag.nodes())
        
        while remaining:
            # Find nodes with all dependencies satisfied
            current_layer = []
            for node in list(remaining):
                if incoming_deps[node].issubset(set(self.dag.nodes()) - remaining):
                    current_layer.append(node)
            
            if current_layer:
                layers.append(current_layer)
                remaining -= set(current_layer)
            else:
                break  # Should not happen in DAG
        
        return layers
    
    def print_detailed_plan(self):
        """Print detailed execution plan"""
        plan = self.get_execution_plan()
        
        print("\n" + "="*60)
        print("📋 DETAILED EXECUTION PLAN")
        print("="*60)
        
        print(f"\n🏗️  Architecture Overview:")
        print(f"  Total Agents: {plan['total_agents']}")
        
        print(f"\n🚀 Execution Layers:")
        for layer_num, agents in sorted(plan['execution_layers'].items()):
            print(f"  Layer {layer_num}:")
            for agent in agents:
                print(f"    • {agent['name']} ({agent['id']})")
        
        print(f"\n🔗 Dependencies:")
        for dep in plan['dependencies']:
            print(f"  {dep['from_name']} → {dep['to_name']}")
            print(f"    Type: {dep['dependency_type']}")
        
        print(f"\n⚡ Parallel Execution Opportunities:")
        for i, group in enumerate(plan['parallelizable_groups']):
            if len(group) > 1:
                print(f"  Group {i+1}: Can run in parallel")
                for agent_id in group:
                    print(f"    • {self.agents[agent_id].agent_name}")
        
        print(f"\n📊 Expected Output:")
        print(f"  • FAQ Page (JSON)")
        print(f"  • Product Description Page (JSON)")
        print(f"  • Comparison Page (JSON)")
        print("="*60)