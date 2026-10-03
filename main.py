from langgraph.graph import StateGraph ,END ,START
from src.Backend.Agents.Extract_prob_type import ask_llm
from src.Backend.Schemas.State import EngineeringState
from src.Backend.Agents.Extract_name_equation import extract_equation_name
from src.pipeline.Workflow import tool_node ,chat_node, format_output_node
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage


graph=StateGraph(EngineeringState)

graph.add_node("extract_problem",ask_llm)
graph.add_node("extract_equation_name",extract_equation_name)
graph.add_node("tool_node",tool_node)
graph.add_node("chat_node" ,chat_node)
graph.add_node("format_output_node", format_output_node)

graph.add_edge(START,"extract_problem")
graph.add_edge("extract_problem","extract_equation_name")
graph.add_edge("extract_equation_name","chat_node")

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

workflow=graph.compile()

from langchain_core.messages import HumanMessage

query = """A mechanical component experiences a force of 1.5 kN applied perpendicularly at a distance of 45 cm from the pivot point. Calculate the resulting torque
"""

init = workflow.invoke(
    {
        "messages": [HumanMessage(content=query)],
        "user_query": query
    },
    config={"recursion_limit": 10} # To prevent infinite loops 
)

print(init["explanation"])
print(50*"=")
print(init["selected_tool"])
print(50*"=")
print(init["validation_result"])
print(50*"=")
print(init["calculation_result"])
