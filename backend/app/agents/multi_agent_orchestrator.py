from typing import List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from typing_extensions import TypedDict
from loguru import logger

from app.agents.adaptive_agent import SalesAgent, OutboundEmailAgent


class AgentState(TypedDict):
    """State shared across agents in the graph"""
    messages: List[Dict[str, str]]
    current_task: str
    context: Dict[str, Any]
    next_agent: Optional[str]
    final_output: Optional[str]


class MultiAgentOrchestrator:
    """Orchestrate multiple agents using LangGraph for complex workflows"""
    
    def __init__(self):
        self.sales_agent = SalesAgent()
        self.email_agent = OutboundEmailAgent()
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build multi-agent coordination graph"""
        workflow = StateGraph(AgentState)
        
        workflow.add_node("router", self._route_task)
        workflow.add_node("sales_agent", self._run_sales_agent)
        workflow.add_node("email_agent", self._run_email_agent)
        workflow.add_node("synthesizer", self._synthesize_results)
        
        workflow.set_entry_point("router")
        
        workflow.add_conditional_edges(
            "router",
            self._decide_next_agent,
            {
                "sales": "sales_agent",
                "email": "email_agent",
                "end": END
            }
        )
        
        workflow.add_edge("sales_agent", "synthesizer")
        workflow.add_edge("email_agent", "synthesizer")
        workflow.add_edge("synthesizer", END)
        
        return workflow.compile()
    
    async def _route_task(self, state: AgentState) -> AgentState:
        """Route task to appropriate agent"""
        logger.info(f"Routing task: {state['current_task']}")
        
        task = state['current_task'].lower()
        
        if "email" in task or "outbound" in task:
            state['next_agent'] = "email"
        elif "sales" in task or "call" in task or "conversation" in task:
            state['next_agent'] = "sales"
        else:
            state['next_agent'] = "sales"
        
        return state
    
    def _decide_next_agent(self, state: AgentState) -> str:
        """Decide which agent to execute next"""
        return state.get('next_agent', 'end')
    
    async def _run_sales_agent(self, state: AgentState) -> AgentState:
        """Execute sales agent"""
        logger.info("Running sales agent")
        result = await self.sales_agent.execute(state['current_task'], state.get('context'))
        state['messages'].append({
            "agent": "sales",
            "output": result.get('output', '')
        })
        return state
    
    async def _run_email_agent(self, state: AgentState) -> AgentState:
        """Execute email agent"""
        logger.info("Running email agent")
        result = await self.email_agent.execute(state['current_task'], state.get('context'))
        state['messages'].append({
            "agent": "email",
            "output": result.get('output', '')
        })
        return state
    
    async def _synthesize_results(self, state: AgentState) -> AgentState:
        """Synthesize results from all agents"""
        logger.info("Synthesizing results")
        
        outputs = [msg['output'] for msg in state['messages'] if 'output' in msg]
        state['final_output'] = "\n\n".join(outputs)
        
        return state
    
    async def execute_workflow(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute multi-agent workflow"""
        initial_state: AgentState = {
            "messages": [],
            "current_task": task,
            "context": context or {},
            "next_agent": None,
            "final_output": None
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "task": task,
            "output": final_state.get('final_output', ''),
            "agent_messages": final_state.get('messages', [])
        }
