from src.Backend.engineering_tools.conversions.mechanics import (
    convert_force,
    convert_mass,
    convert_acceleration,
    convert_torque,
    convert_work,
    convert_energy,
    convert_power,
    convert_stress,
    convert_strain,
)
from src.Backend.engineering_tools.mechanics.MechanicsCalculator import (
    calculate_force,
    calculate_mass,
    calculate_acceleration,
    calculate_torque,
    calculate_work,
    calculate_energy,
    calculate_power,
    calculate_stress,
    calculate_strain,
)

from langgraph.prebuilt import ToolNode ,tools_condition
from src.Exceptions import MechMind
from src.Logger import logging
from src.Backend.Schemas.State import EngineeringState
from langchain_groq import ChatGroq
import sys
import yaml
from src.Backend.Schemas.State import CalculationOutput
from langchain_openrouter import ChatOpenRouter
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.Call_Models import call_models


MECHANICS_TOOLS = [
    calculate_force,
    calculate_mass,
    calculate_acceleration,
    calculate_torque,
    calculate_work,
    calculate_energy,
    calculate_power,
    calculate_stress,
    calculate_strain,

    convert_force,
    convert_mass,
    convert_acceleration,
    convert_torque,
    convert_work,
    convert_energy,
    convert_power,
    convert_stress,
    convert_strain,
]


# In Extract_prob_type.py

# Create an instance of call_models
models = call_models()

# Call the instance method
llm = models.call_groq()


############################

llm_with_tools = llm.bind_tools(MECHANICS_TOOLS)

logging.info("create llm node....")

def chat_node(state: EngineeringState):
    """
    LLM node that analyzes the engineering problem
    and may request one or more tools.
    """
    try:
        messages = state.get("messages", [])
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    except Exception as e:
        logging.error("Error occurred inside chat_node")
        raise MechMind(e, sys)

tool_node = ToolNode(MECHANICS_TOOLS)

logging.info("create format_output_node....")

def format_output_node(state: EngineeringState):
    """
    Extracts final structured output from the conversation.
    """
    try:
        messages = state.get("messages", [])
        structured_llm = llm.with_structured_output(CalculationOutput)
        
        response = structured_llm.invoke(
            [{"role": "system", "content": "Extract the selected tool, calculation results, validation info, and explanation based on the conversation."}] + messages
        )
        
        return {
            "selected_tool": response.selected_tool,
            "calculation_result": response.calculation_result,
            "validation_result": response.validation_result,
            "explanation": response.explanation
        }
    except Exception as e:
        logging.error("Error occurred inside format_output_node")
        raise MechMind(e, sys)