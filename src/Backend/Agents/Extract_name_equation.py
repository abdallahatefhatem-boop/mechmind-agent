from src.Backend.Schemas.State import EngineeringState,EquationSelectionOutput
from src.Logger import logging
from src.Exceptions import MechMind
from dotenv import load_dotenv
from src.utils.Call_Models import call_models
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser ,JsonOutputParser
import yaml
import sys
from src.utils.from_config import Prompt_tempelet ,supported_operations

# Load environment variables first
load_dotenv()

# calling llm
# In Extract_prob_type.py

# Create an instance of call_models
models = call_models()

# Call the instance method
llm = models.call_google()

# prompt

prompt_choose_equation=Prompt_tempelet.System_choose_Equation()



structured_llm = llm.with_structured_output(EquationSelectionOutput)


def extract_equation_name(state: EngineeringState):
    try:
        user_message = state["user_query"]
        problem_type = state["problem_type"]
        operations = supported_operations.problem_type(problem_type=problem_type)
        system_prompt = prompt_choose_equation

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{user_message}")
        ])

        
        chain = prompt | structured_llm

        
        result: EquationSelectionOutput = chain.invoke({
            "problem_type": problem_type,
            "operations": operations,
            "user_message": user_message
        })

       
        return {
            "operation": result.operation,
            "parameters": result.parameters,  
            "units": result.units
        }

    except Exception as e:
        logging.error("Error occurred inside extract_equation_name function")
        raise MechMind(e, sys)




