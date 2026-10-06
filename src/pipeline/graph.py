from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

from src.Backend.Agents.Extract_prob_type import ask_llm
from src.Backend.Schemas.State import EngineeringState
from src.Backend.Agents.Extract_name_equation import extract_equation_name
from src.pipeline.Workflow import tool_node, chat_node, format_output_node, general_chat_node, route_query
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage
from ensure import ensure_annotations

DB_URI = "postgresql://postgres:postgres@localhost:5432/engineering_db"

# Establish Postgres connection pool for thread safety
pool = ConnectionPool(DB_URI)
checkpointer = PostgresSaver(pool)
checkpointer.setup()

# Build Graph
graph = StateGraph(EngineeringState)

graph.add_node("extract_problem", ask_llm)
graph.add_node("extract_equation_name", extract_equation_name)
graph.add_node("tool_node", tool_node)
graph.add_node("chat_node", chat_node)
graph.add_node("format_output_node", format_output_node)
graph.add_node("general_chat_node", general_chat_node)

graph.add_conditional_edges(
    START,
    route_query,
    {
        "extract_problem": "extract_problem",
        "general_chat_node": "general_chat_node",
    }
)
graph.add_edge("general_chat_node", END)
graph.add_edge("extract_problem", "extract_equation_name")
graph.add_edge("extract_equation_name", "chat_node")

graph.add_conditional_edges(
    "chat_node",
    tools_condition,
    {
        "tools": "tool_node",
        "__end__": "format_output_node",
    }
)
graph.add_edge("format_output_node", END)
graph.add_edge("tool_node", "chat_node")    

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