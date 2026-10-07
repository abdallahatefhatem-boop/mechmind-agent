from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from src.Backend.Agents.Extract_prob_type import ask_llm
from src.Backend.Schemas.State import EngineeringState
from src.Backend.Agents.Extract_name_equation import extract_equation_name
from src.pipeline.Workflow import tool_node, chat_node, format_output_node, chat_response_node
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage
from ensure import ensure_annotations

DB_URI = "postgresql://postgres:postgres@localhost:5432/engineering_db"

pool = ConnectionPool(DB_URI, kwargs={"autocommit": True})
checkpointer = PostgresSaver(pool)
checkpointer.setup()

graph = StateGraph(EngineeringState)

# Add Nodes
graph.add_node("extract_problem", ask_llm)
graph.add_node("extract_equation_name", extract_equation_name)
graph.add_node("tool_node", tool_node)
graph.add_node("chat_node", chat_node)
graph.add_node("format_output_node", format_output_node)
graph.add_node("chat_response_node", chat_response_node)

# Router function to skip equation extraction for non-engineering queries
def route_after_problem_extraction(state: EngineeringState) -> str:
    problem_type = state.get("problem_type", [])
    if isinstance(problem_type, str):
        problem_type = [problem_type]
    
    # If no engineering problem is detected (e.g. "hi", "what is your name")
    if "noproblem" in problem_type or not problem_type:
        return "chat_node"
    
    return "extract_equation_name"

# Define Edges
graph.add_edge(START, "extract_problem")

# Conditional edge based on query type
graph.add_conditional_edges(
    "extract_problem",
    route_after_problem_extraction,
    {
        "chat_node": "chat_node",
        "extract_equation_name": "extract_equation_name"
    }
)

graph.add_edge("extract_equation_name", "chat_node")

# Conditional routing for tool calling vs answering directly
graph.add_conditional_edges(
    "chat_node",
    tools_condition,
    {
        "tools": "tool_node",
        "__end__": "chat_response_node",  # no tool call → plain reply
    }
)

graph.add_edge("tool_node", "format_output_node")

graph.add_edge("chat_response_node", END)
graph.add_edge("format_output_node", END)

workflow = graph.compile(checkpointer=checkpointer)

@ensure_annotations
def run_workflow(query: str, thread_id: str = "default_session"):
    config = {
        "recursion_limit": 25,
        "configurable": {"thread_id": thread_id}
    }
    
    init = workflow.invoke(
        {
            "messages": [HumanMessage(content=query)],
            "user_query": query
        },
        config=config
    )
    
    return {
        "explanation": init.get("explanation"),
        "selected_tool": init.get("selected_tool"),
        "validation_result": init.get("validation_result"),
        "calculation_result": init.get("calculation_result")
    }