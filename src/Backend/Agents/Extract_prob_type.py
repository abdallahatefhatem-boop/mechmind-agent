import sys
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.Exceptions import MechMind
from src.Logger import logging
from src.Backend.Schemas.State import EngineeringState
from src.utils.Call_Models import call_models
from src.utils.from_config import Prompt_tempelet

# Load environment variables first
load_dotenv()

# Initialize LLM model
models = call_models()
llm = models.call_google()

# Load system prompt
prompt_choose_prob = Prompt_tempelet.System_choose_prob()


# Pydantic schema to enforce list structured output from LLM
class ProblemTypeOutput(BaseModel):
    problem_type: list[str] = Field(
        description="List of identified mechanical engineering problem types strictly matching the available configuration keys if there isn't any problem tell noproblem."
    )


def ask_llm(state: EngineeringState):
    try:
        user_message = state["user_query"]
        system_prompt = prompt_choose_prob

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{user_message}")
        ])

        # Enforce structured output to prevent parsing errors and markdown code blocks
        structured_llm = llm.with_structured_output(ProblemTypeOutput)
        chain = prompt | structured_llm

        response: ProblemTypeOutput = chain.invoke({"user_message": user_message})

        # Return problem_type as list[str] to match EngineeringState
        return {"problem_type": response.problem_type}

    except Exception as e:
        logging.error("Error occurred inside ask_llm function")
        raise MechMind(e, sys)