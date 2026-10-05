import sys
import yaml
from src.Exceptions import MechMind
from src.Logger import logging

# Prompt configuration loading
try:
    logging.info("Reading prompts from config/Prompts.yaml...")
    with open(file="config/Prompts.yaml", mode="r") as f:
        prompt_config = yaml.safe_load(f)
    logging.info("Prompts loaded successfully.")
except Exception as e:
    logging.error("Failed to read config/Prompts.yaml")
    raise MechMind(e, sys)


class Prompt_tempelet:
    @staticmethod
    def System_choose_prob():
        choose_prob = prompt_config["Write_Prompt"]["System_choose_prob"]
        return choose_prob

    @staticmethod
    def System_choose_Equation():
        choose_equation = prompt_config["Write_Prompt"]["System_choose_Equation"]
        return choose_equation


# Problem type configuration loading
try:
    logging.info("Reading name of equations from config/Problem_type.yaml...")
    with open(file="config/Problem_type.yaml", mode="r") as f:
        name_equations = yaml.safe_load(f)
    logging.info("Name of Equations loaded successfully.")
except Exception as e:
    logging.error("Failed to read config/Problem_type.yaml")
    raise MechMind(e, sys)


class supported_operations:
    @staticmethod
    def problem_type(problem_type):
        """
        Retrieves supported operations for given problem type(s).
        Handles str, list of str, or None safely.
        """
        # Ensure problem_type is treated as a list
        if isinstance(problem_type, str):
            problem_type = [problem_type]
        elif problem_type is None:
            problem_type = []

        combined_operations = {}

        # Loop through each problem type in the list and gather operations
        for p_type in problem_type:
            if p_type in name_equations.get("problems", {}):
                ops = name_equations["problems"][p_type].get("supported_operations", [])
                combined_operations[p_type] = ops
            else:
                logging.warning(f"Problem type '{p_type}' not found in configuration.")

        return combined_operations