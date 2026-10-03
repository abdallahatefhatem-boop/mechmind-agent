import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openrouter import ChatOpenRouter
from langchain_groq import ChatGroq
from src.Exceptions import MechMind
from src.Logger import logging
import sys
from dotenv import load_dotenv
load_dotenv()

try:
    logging.info("Reading model configuration from yaml...")
    file_path = "config/model_name.yaml"
    with open(file=file_path, mode="r") as f:
        model_name = yaml.safe_load(f)
    logging.info("Model configuration loaded successfully.")
except Exception as e:
    logging.error("Failed to read config/model_name.yaml")
    raise MechMind(e, sys)



"""
name_Groq: "qwen/qwen3.8-27b"
  name_OpenRouter_google: "google/gemma-4-31b-it:free"
  name_OpenRouter_groq: "qwen/qwen3.8-27b:free"
  name_google: "gemini-flash-lite-latest" 
  """

class call_models:
    def __init__(self):
        self.google=model_name["LLM"]["name_google"]
        self.groq=model_name["LLM"]["name_Groq"]
        self.openrouter_groq=model_name["LLM"]["name_OpenRouter_groq"]
        self.openrouter_google=model_name["LLM"]["name_OpenRouter_google"]


    def call_google(self):
        llm=ChatGoogleGenerativeAI(model=self.google)
        return llm

    def call_groq(self):
        llm=ChatGroq(model=self.groq)
        return llm
    
    def call_openrouter_google(self):
        llm=ChatOpenRouter(model=self.openrouter_google)
        return llm
    
    def call_openrouter_groq(self):
        llm=ChatOpenRouter(model=self.openrouter_groq)
        return llm