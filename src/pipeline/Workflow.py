import sys
from typing import Dict, Any

from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from src.Exceptions import MechMind
from src.Logger import logging
from src.Backend.Schemas.State import EngineeringState, CalculationOutput
from src.utils.Call_Models import call_models

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

        # Build a detailed system message passing parameters alongside their units
        system_content = (
            "You are an expert Mechanical Engineering Assistant.\n\n"
            f"Problem Categories: {problem_type}\n"
            f"Target Operations: {operations}\n"
            f"Extracted Parameters: {parameters}\n"
            f"Associated Units: {units}\n\n"
            "Instructions:\n"
            "1. Review the target operations and extracted parameters along with their specific units.\n"
            "2. Convert parameter units if needed before performing calculations.\n"
            "3. Invoke the necessary calculation/conversion tools using the exact numerical values and appropriate units.\n"
            "4. If multiple operations are required, execute all relevant tools in proper sequence.\n"
            "5. Do not invent or fabricate missing parameters."
        )

        system_message = SystemMessage(content=system_content)
        full_messages = [system_message] + messages

        response = llm_with_tools.invoke(full_messages)
        return {"messages": [response]}

    except Exception as e:
        logging.error("Error occurred inside chat_node")
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

        system_prompt = (
            "You are a mechanical engineering output formatter.\n"
            "Analyze the conversation history, tool calls, and results.\n\n"
            f"Parameters: {parameters}\n"
            f"Units: {units}\n"
            f"Operations: {operations}\n\n"
            "Return a valid JSON object matching this schema EXACTLY:\n"
            "{\n"
            '  "selected_tool": ["tool_name"],\n'
            '  "calculation_result": {"parameter_name": value},\n'
            '  "validation_result": {"valid": true, "warnings": []},\n'
            '  "explanation": "Brief step-by-step summary of formulas and calculations."\n'
            "}\n\n"
            "Keep 'explanation' concise to ensure valid JSON generation."
        )

        prompt_messages = [{"role": "system", "content": system_prompt}] + messages

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