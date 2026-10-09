import sys
from typing import Dict, Any, List

from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, ToolMessage
from langchain_core.output_parsers import PydanticOutputParser
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
    based on state problem_types and operations.

    Matching uses three tiers for robustness:
      Tier 1 – exact string match     (e.g. 'shaft_design' == 'shaft_design')
      Tier 2 – word-stem match        (e.g. 'shaft_design' vs 'shaft_diameter'
                                        share the word 'shaft' → match)
      Tier 3 – substring match        (original fallback behaviour)

    Base mechanics + unit_conversion are always appended so the LLM always
    has access to fundamental tools regardless of the specialist match.
    """
    selected_tools = []

    # Normalize inputs
    keys_to_check = [str(k).lower().strip() for k in (problem_types + operations) if k]

    # Generic words that alone should not trigger a specialist-tool match
    NOISE_WORDS = {"design", "calculation", "compute", "get", "find", "calculate"}

    for key, tools in TOOL_MAPPING.items():
        matched = False
        for query_key in keys_to_check:
            # Tier 1 – exact match
            if key == query_key:
                matched = True
                break

            # Tier 2 – shared meaningful word-stem
            # e.g. "shaft_design" ∩ "shaft_diameter" = {"shaft"} → True
            key_words = set(key.split("_")) - NOISE_WORDS
            query_words = set(query_key.split("_")) - NOISE_WORDS
            if key_words & query_words:
                matched = True
                break

            # Tier 3 – substring match (legacy fallback)
            if key in query_key or query_key in key:
                matched = True
                break

        if matched:
            selected_tools.extend(tools)

    # Always include base mechanics + unit_conversion tools
    selected_tools.extend(TOOL_MAPPING["mechanics"])
    selected_tools.extend(TOOL_MAPPING["unit_conversion"])

    # Deduplicate while preserving order
    unique_tools = []
    seen_names: set = set()
    for tool in selected_tools:
        tool_name = getattr(tool, "name", str(tool))
        if tool_name not in seen_names:
            seen_names.add(tool_name)
            unique_tools.append(tool)

    return unique_tools


def chat_node(state: EngineeringState) -> Dict[str, Any]:
    """
    LLM node that dynamically binds only relevant tools to stay within the
    Groq TPM token limit (8000) while guaranteeing the right tools are included.

    Tool selection uses two phases:
      Phase 1 – Direct lookup:  problem_type keys map directly to TOOL_MAPPING,
                so problem_type=['shaft_design'] always includes shaft_design.
      Phase 2 – Fuzzy match:   operations are matched via word-stem matching
                as a secondary safety net.
    Base mechanics + unit_conversion tools are always appended.
    """
    try:
        messages = state.get("messages", [])
        problem_type = state.get("problem_type", []) or []
        operations = state.get("operation", []) or []
        parameters = state.get("parameters", {})
        units = state.get("units", {})

        # Smart dynamic filtering — stays within token limits
        active_tools = filter_tools_by_state(problem_type, operations)

        llm_with_tools = llm.bind_tools(active_tools)

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


def sanitize_messages_for_extraction(messages: List[Any]) -> List[Any]:
    """
    Converts a raw LangGraph message list into a form that is safe for
    structured output extraction (no ToolMessages, no bare tool_call AIMessages).

    Mapping:
      HumanMessage            → kept as-is
      AIMessage (tool_calls)  → converted to plain AIMessage summarising the call
      ToolMessage             → converted to HumanMessage relaying the result
      AIMessage (plain)       → kept as-is
    """
    safe: List[Any] = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            # Surface the tool result as readable context for the formatter
            safe.append(
                HumanMessage(
                    content=f"[Tool result for '{msg.name}']:\n{msg.content}"
                )
            )
        elif isinstance(msg, AIMessage):
            if msg.tool_calls:
                # Summarise what tools were invoked instead of passing raw tool_calls
                call_summary = ", ".join(
                    f"{tc['name']}({tc.get('args', {})})"
                    for tc in msg.tool_calls
                )
                safe.append(
                    AIMessage(content=f"[Called tools]: {call_summary}")
                )
            else:
                safe.append(msg)
        else:
            # HumanMessage and any other message types are kept as-is
            safe.append(msg)
    return safe


def format_output_node(state: EngineeringState) -> Dict[str, Any]:
    """
    Extracts structured final output using CalculationOutput schema.
    Uses PydanticOutputParser to extract the JSON directly from the raw message
    content, bypassing flaky tool-calling API enforcement.
    """
    try:
        messages = state.get("messages", [])
        parameters = state.get("parameters", {})
        units = state.get("units", {})
        operations = state.get("operation", [])

        raw_format_prompt = Prompt_tempelet.format_output()
        system_prompt = raw_format_prompt.format(
            parameters=parameters,
            units=units,
            operations=operations,
        )

        # Strip ToolMessages / bare tool-call AIMessages before extraction
        safe_messages = sanitize_messages_for_extraction(messages)
        prompt_messages = [SystemMessage(content=system_prompt)] + safe_messages

        # Invoke raw LLM (no tool-calling enforcement)
        response_msg = llm.invoke(prompt_messages)

        # Parse the raw text content into the Pydantic schema
        parser = PydanticOutputParser(pydantic_object=CalculationOutput)
        
        try:
            response = parser.parse(response_msg.content)
        except Exception as parse_error:
            # Fallback if the LLM output something slightly malformed
            import json, re
            match = re.search(r'\{.*\}', response_msg.content, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                response = CalculationOutput(**data)
            else:
                raise parse_error

        return {
            "selected_tool": response.selected_tool,
            "calculation_result": response.calculation_result,
            "validation_result": response.validation_result,
            "explanation": response.explanation,
        }

    except Exception as e:
        logging.error("Error occurred inside format_output_node")
        raise MechMind(e, sys)