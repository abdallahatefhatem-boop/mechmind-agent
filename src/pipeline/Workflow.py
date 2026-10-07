import sys
from langchain_core.messages import AIMessage
from typing import Dict, Any

from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from src.Exceptions import MechMind
from src.Logger import logging
from src.Backend.Schemas.State import EngineeringState, CalculationOutput
from src.utils.Call_Models import call_models
from src.utils.from_config import Prompt_tempelet

# Import mechanical tools and converters
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

# Aggregate available tools
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

# Initialize model and tools
models = call_models()
llm = models.call_groq()
llm_with_tools = llm.bind_tools(MECHANICS_TOOLS)

tool_node = ToolNode(MECHANICS_TOOLS)



def chat_node(state: EngineeringState) -> Dict[str, Any]:
    """
    LLM node that uses the extracted problem types, operations, parameters,
    and units to select and execute the required engineering tools.
    """
    try:
        messages = state.get("messages", [])
        problem_type = state.get("problem_type", [])
        operations = state.get("operation", [])
        parameters = state.get("parameters", {})
        units = state.get("units", {})


        raw_system_content = Prompt_tempelet.system_content()
        system_content = raw_system_content.format(
            problem_type=problem_type,
            operations=operations,
            parameters=parameters,
            units=units,
        )

        system_message = SystemMessage(content=system_content)
        full_messages = [system_message] + messages

        response = llm_with_tools.invoke(full_messages)
        return {"messages": [response]}

    except Exception as e:
        logging.error("Error occurred inside chat_node")
        raise MechMind(e, sys)


def chat_response_node(state: EngineeringState) -> Dict[str, Any]:
    """
    Handles non-engineering queries (greetings, general questions).
    Returns the LLM's last message as a plain explanation without
    requiring the CalculationOutput structured schema.
    """
    try:
        messages = state.get("messages", [])
        # Get the last AI message content as the plain reply
        last_ai_msg = next(
            (m for m in reversed(messages) if isinstance(m, AIMessage)),
            None
        )
        explanation = last_ai_msg.content if last_ai_msg else "I'm here to help!"
        return {
            "explanation": explanation,
            "selected_tool": [],
            "calculation_result": {},
            "validation_result": {"valid": True, "warnings": []},
        }
    except Exception as e:
        logging.error("Error occurred inside chat_response_node")
        raise MechMind(e, sys)



def format_output_node(state: EngineeringState) -> Dict[str, Any]:
    """
    Extracts structured final output using CalculationOutput schema with json_mode.
    """
    try:
        messages = state.get("messages", [])
        parameters = state.get("parameters", {})
        units = state.get("units", {})
        operations = state.get("operation", [])

        # Configure structured output with json_mode
        structured_llm = llm.with_structured_output(
            CalculationOutput,
            method="json_mode"
        )

        
        raw_format_prompt = Prompt_tempelet.format_output()
        system_prompt = raw_format_prompt.format(
            parameters=parameters,
            units=units,
            operations=operations,
        )
        prompt_messages = [SystemMessage(content=system_prompt)] + messages

        response: CalculationOutput = structured_llm.invoke(prompt_messages)

        return {
            "selected_tool": response.selected_tool,
            "calculation_result": response.calculation_result,
            "validation_result": response.validation_result,
            "explanation": response.explanation,
        }

    except Exception as e:
        logging.error("Error occurred inside format_output_node")
        raise MechMind(e, sys)