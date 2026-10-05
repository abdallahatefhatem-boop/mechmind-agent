from typing import TypedDict, Annotated ,Dict,List ,Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field 



class EngineeringState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]

    # The original question/problem provided by the user
    # Example: "Calculate the bending stress of a beam"
    user_query: str

    # The type/category of the engineering problem
    # Example: "beam_stress", "shaft_design", "fluid_flow"
    problem_type: Optional[list[str]]

    
    # Example: "bending_stress", "shaft_diameter"
    operation:Optional[list[str]]

    # The input values extracted from the user's question
    # Example: {"force": 1000, "length": 2, "diameter": 0.05}
    parameters: dict

    # The units associated with each parameter
    # Example: {"force": "N", "length": "m", "diameter": "mm"}
    units: dict

    # The engineering tool/function selected to solve the problem
    # Example: "calculate_beam_stress"
    selected_tool: Optional[list[str]]

    # The result returned by the engineering calculation tool
    # Example: {"stress": 25e6, "unit": "Pa"}
    calculation_result: dict

    # Stores the result of validating the inputs and calculation
    # Example: {"valid": True, "warnings": []}
    validation_result: dict

    # The final human-readable explanation generated for the user
    # Contains the formula, inputs, calculation, result, and assumptions
    explanation: str


class MessageState(TypedDict):

    # Stores the conversation history between the user, AI, and tools
    # BaseMessage can represent HumanMessage, AIMessage, ToolMessage, etc.
    #
    # add_messages tells LangGraph how to update the message history:
    # new messages are added/merged instead of simply replacing the old ones.
    messages: Annotated[list[BaseMessage], add_messages]





class EquationSelectionOutput(BaseModel):
    operation: List[str] = Field(
        description=(
            "List of calculation operations required to solve the user's problem. "
            "Every operation MUST be selected from the available supported operations. "
            "Never invent operation names."
        )
    )

    parameters: Optional[Dict[str, float]] = Field(
        default=None,
        description=(
            "Extracted numerical parameters from the user's query. "
            "Material properties such as ultimate_strength are parameters, "
            "not operations."
        )
    )

    units: Optional[Dict[str, str]] = Field(
        default=None,
        description="Units extracted for each parameter."
    )


class CalculationOutput(BaseModel):
    selected_tool: List[str] = Field(
        default_factory=list,
        description="List of engineering tools used."
    )
    calculation_result: Dict = Field(
        default_factory=dict,
        description="Numerical outputs and units."
    )
    validation_result: Dict = Field(
        default_factory=lambda: {"valid": True, "warnings": []},
        description="Validation status and warnings."
    )
    explanation: str = Field(
        default="Step-by-step engineering calculation completed.",
        description="Concise summary of the solution process."
    )
    