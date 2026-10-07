import sys
import yaml
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from src.Backend.Schemas.State import EngineeringState, EquationSelectionOutput
from src.Exceptions import MechMind
from src.Logger import logging
from src.utils.Call_Models import call_models
from src.utils.from_config import Prompt_tempelet, supported_operations

# Load environment variables first
load_dotenv()

# Initialize LLM model
models = call_models()
llm = models.call_google()

# Load system prompt template
prompt_choose_equation = Prompt_tempelet.System_choose_Equation()

# Bind structured output model to EquationSelectionOutput schema
structured_llm = llm.with_structured_output(EquationSelectionOutput)


def extract_equation_name(state: EngineeringState) -> dict:
    try:
        user_message = state["user_query"]
        
        # Ensure problem_type is formatted as a list
        problem_type = state.get("problem_type", [])
        if isinstance(problem_type, str):
            problem_type = [problem_type]
        if "noproblem" in problem_type:
            return {"operation": "noproblem", "parameters": {}, "units": {}}

        
        else:
            # Retrieve available operations for all identified problem types
            operations = supported_operations.problem_type(problem_type=problem_type)
            system_prompt = prompt_choose_equation

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{user_message}")
            ])

            chain = prompt | structured_llm

            # Invoke the chain passing problem_type, operations, and user query
            result: EquationSelectionOutput = chain.invoke({
                "problem_type": problem_type,
                "operations": operations,
                "user_message": user_message
            })

            # Return extracted details matching state schema
            return {
                "operation": result.operation,
                "parameters": result.parameters or {},
                "units": result.units or {}
            }

    except Exception as e:
        logging.error("Error occurred inside extract_equation_name function")
        raise MechMind(e, sys)