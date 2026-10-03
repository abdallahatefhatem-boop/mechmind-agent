import sys
import yaml
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser ,JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from src.Exceptions import MechMind
from src.Logger import logging
from src.Backend.Schemas.State import EngineeringState
from src.utils.Call_Models import call_models
from src.utils.from_config import Prompt_tempelet




# Load environment variables first
load_dotenv()

# calling the llm
# In Extract_prob_type.py

# Create an instance of call_models
models = call_models()

# Call the instance method
llm = models.call_google()

# prompt

prompt_choose_prob=Prompt_tempelet.System_choose_prob()





def ask_llm(state: EngineeringState):
    try:
        user_message = state["user_query"]
        system_prompt =prompt_choose_prob

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt), 
            ("human", "{user_message}")
        ])

        chain = prompt | llm | StrOutputParser()

        response = chain.invoke({"user_message": user_message})

        return {"problem_type": response}
    
    
    except Exception as e:
        logging.error("Error occurred inside ask_llm function")
        raise MechMind(e, sys)