import sys
from typing import Dict, Any, List

from langchain_core.messages import SystemMessage, AIMessage
from langgraph.prebuilt import ToolNode
from src.Exceptions import MechMind
from src.Logger import logging
from src.Backend.Schemas.State import EngineeringState, CalculationOutput
from src.utils.Call_Models import call_models
from src.utils.from_config import Prompt_tempelet

# Import mechanical tools and converters
from src.Backend.engineering_tools.conversions.unit_converter import (
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
from src.Backend.engineering_tools.mechanics.factor_of_safety import factor_of_safety
from src.Backend.engineering_tools.mechanics.beam_deflection import beam_deflection
from src.Backend.engineering_tools.mechanics.beam_stress import beam_stress
from src.Backend.engineering_tools.mechanics.bearing_life import bearing_life
from src.Backend.engineering_tools.mechanics.bolt_strength import bolt_strength
from src.Backend.engineering_tools.mechanics.column_buckling import column_buckling
from src.Backend.engineering_tools.mechanics.fatigue_life import fatigue_life
from src.Backend.engineering_tools.mechanics.fluid_flow import fluid_flow
from src.Backend.engineering_tools.mechanics.gear_design import gear_design
from src.Backend.engineering_tools.mechanics.heat_transfer import heat_transfer
from src.Backend.engineering_tools.mechanics.hvac_load import hvac_load
from src.Backend.engineering_tools.mechanics.pressure_vessel import pressure_vessel
from src.Backend.engineering_tools.mechanics.pump_power import pump_power
from src.Backend.engineering_tools.mechanics.shaft_design import shaft_design
from src.Backend.engineering_tools.mechanics.spring_design import spring_design
from src.Backend.engineering_tools.mechanics.thermal_expansion import thermal_expansion
from src.Backend.engineering_tools.mechanics.thermodynamics import thermodynamics


# Map categories/keys (problem_type/operation) to their specific Python tools
TOOL_MAPPING = {
    # Basic Mechanics
    "mechanics": [
        calculate_force, calculate_mass, calculate_acceleration, 
        calculate_torque, calculate_work, calculate_energy, 
        calculate_power, calculate_stress, calculate_strain
    ],
    # Unit Converters
    "unit_conversion": [
        convert_force, convert_mass, convert_acceleration, 
        convert_torque, convert_work, convert_energy, 
        convert_power, convert_stress, convert_strain
    ],
    # Specialized Engineering Tools
    "factor_of_safety": [factor_of_safety],
    "beam_stress": [beam_stress],
    "beam_deflection": [beam_deflection],
    "column_buckling": [column_buckling],
    "fatigue_life": [fatigue_life],
    "shaft_design": [shaft_design],
    "gear_design": [gear_design],
    "bearing_life": [bearing_life],
    "spring_design": [spring_design],
    "bolt_strength": [bolt_strength],
    "pressure_vessel": [pressure_vessel],
    "fluid_flow": [fluid_flow],
    "pump_power": [pump_power],
    "thermodynamics": [thermodynamics],
    "thermal_expansion": [thermal_expansion],
    "heat_transfer": [heat_transfer],
    "hvac_load": [hvac_load],
}

# Full list of available tools for ToolNode graph execution
ALL_MECHANICS_TOOLS = [
    calculate_force, calculate_mass, calculate_acceleration, calculate_torque,
    calculate_work, calculate_energy, calculate_power, calculate_stress, calculate_strain,
    convert_force, convert_mass, convert_acceleration, convert_torque, convert_work,
    convert_energy, convert_power, convert_stress, convert_strain,
    factor_of_safety, beam_deflection, beam_stress, bearing_life, bolt_strength,
    column_buckling, fatigue_life, fluid_flow, gear_design, heat_transfer,
    hvac_load, pressure_vessel, pump_power, shaft_design, spring_design,
    thermal_expansion, thermodynamics
]

# Initialize model & ToolNode
models = call_models()
llm = models.call_groq()

# ToolNode maintains all tools so LangGraph can execute any selected tool
tool_node = ToolNode(ALL_MECHANICS_TOOLS)


def filter_tools_by_state(problem_types: List[str], operations: List[str]) -> List[Any]:
    """
    Dynamically filters and returns only relevant tools 
    based on state problem_types and operations without unhashable errors.
    """
    selected_tools = []
    
    # Normalize strings for matching
    keys_to_check = [str(k).lower().strip() for k in (problem_types + operations) if k]

    for key, tools in TOOL_MAPPING.items():
        for query_key in keys_to_check:
            if key in query_key or query_key in key:
                selected_tools.extend(tools)

    # Fallback if no specific match was found
    if not selected_tools:
        selected_tools.extend(TOOL_MAPPING["mechanics"])
        selected_tools.extend(TOOL_MAPPING["unit_conversion"])

    # Remove duplicates safely using tool.name instead of set()
    unique_tools = []
    seen_names = set()
    for tool in selected_tools:
        tool_name = getattr(tool, "name", str(tool))
        if tool_name not in seen_names:
            seen_names.add(tool_name)
            unique_tools.append(tool)

    return unique_tools


def chat_node(state: EngineeringState) -> Dict[str, Any]:
    """
    LLM node that dynamically binds only relevant tools 
    based on the extracted problem types and operations.
    """
    try:
        messages = state.get("messages", [])
        problem_type = state.get("problem_type", []) or []
        operations = state.get("operation", []) or []
        parameters = state.get("parameters", {})
        units = state.get("units", {})

        # 1. Dynamically filter tools to prevent token overflow
        active_tools = filter_tools_by_state(problem_type, operations)

        # 2. Bind only filtered tools for the current call
        llm_with_tools = llm.bind_tools(active_tools)

        # 3. Format system message and invoke model
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