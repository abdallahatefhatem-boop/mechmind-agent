import yaml
from src.Logger import logging
from src.Exceptions import MechMind
import sys

#prompt
###################
try:
    logging.info("Reading prompts from config/Prompts.yaml...")
    with open(file="config/Prompts.yaml", mode="r") as f:
        prompt_config = yaml.safe_load(f)
    logging.info("Prompts loaded successfully.")
except Exception as e:
    logging.error("Failed to read config/Prompts.yaml")
    raise MechMind(e, sys)



# class
class Prompt_tempelet:
    def System_choose_prob():
        choose_prob=prompt_config["Write_Prompt"]["System_choose_prob"]
        return choose_prob

    def System_choose_Equation():
        choose_equation=prompt_config["Write_Prompt"]["System_choose_Equation"]
        return choose_equation


#problem type
##################
try:
    logging.info("Reading name of equations from config/Problem_type.yaml...")
    with open(file="config/Problem_type.yaml", mode="r") as f:
        name_equations = yaml.safe_load(f)
    logging.info("Name of Equations loaded successfully.")
except Exception as e:
    logging.error("Failed to read config/Problem_type.yaml")
    raise MechMind(e, sys)




class supported_operations:
    def problem_type(problem_type):
        type_problem=name_equations["problems"][problem_type]["supported_operations"]

        return type_problem