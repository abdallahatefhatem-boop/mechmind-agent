from langgraph.graph import StateGraph ,END ,START
from src.Backend.Agents.Extract_prob_type import ask_llm
from src.Backend.Schemas.State import EngineeringState
from src.Backend.Agents.Extract_name_equation import extract_equation_name
from src.pipeline.Workflow import tool_node ,chat_node, format_output_node
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage
from ensure import ensure_annotations


graph=StateGraph(EngineeringState)

graph.add_node("extract_problem",ask_llm)
graph.add_node("extract_equation_name",extract_equation_name)


graph.add_edge(START,"extract_problem")
graph.add_edge("extract_problem","extract_equation_name")
graph.add_edge("extract_equation_name",END)


workflow=graph.compile()

@ensure_annotations # to ensure the input will be string not anything else
def ask_llm(query:str):

    init = workflow.invoke(
        {
            "messages": [HumanMessage(content=query)],
            "user_query": query
        },
        config={"recursion_limit": 10} # To prevent infinite loops 
    )
    return init

p=ask_llm(
  "A 20 kg block A rests on a rough horizontal table and is connected by a massless, inextensible cable to a 10 kg block B hanging vertically over a solid-disk pulley. The pulley has a mass of 6 kg and a radius of 0.20 m, with moment of inertia I = (1/2)MR². The coefficient of kinetic friction between block A and the table is 0.25. A constant horizontal force of 35 N is applied to block A in the direction away from the pulley. The cable does not slip on the pulley, and the pulley axle is frictionless. The system starts from rest and block A moves 2 m toward the pulley. Take g = 9.81 m/s².\n\nDetermine the direction of motion, the linear acceleration of blocks A and B, the angular acceleration of the pulley, the tension in each side of the cable, the kinetic friction force, the final velocity of the blocks, the work done by the applied force, the work done by friction, the change in kinetic energy of the system, and the final rotational kinetic energy of the pulley. Show the governing equations and verify the results using Newton's second law, the rotational equation of motion, the no-slip constraint, and the work-energy principle."
)
print(p)