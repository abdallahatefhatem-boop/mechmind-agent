from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Optional
import sys
from src.pipeline.graph import ask_llm
from src.Logger import logger
from src.Exceptions import MechMind

router = APIRouter()

class QueryRequest(BaseModel): # input user question
    query: str

class QueryResponse(BaseModel):# output
    explanation: str
    selected_tool: Optional[str] = None
    validation_result: Optional[Any] = None
    calculation_result: Optional[Any] = None

@router.post("/ask", response_model=QueryResponse)
async def ask_engineering_question(request: QueryRequest):
    try:
        logger.info(f"Received query: {request.query}")
        
        # Call the langgraph workflow
        result = ask_llm(request.query)
        
        logger.info("Successfully processed query.")
        
        # Map the dictionary returned by ask_llm to our Pydantic model
        return QueryResponse(
            explanation=result.get("expentaion", ""),
            selected_tool=result.get("select_tool"),
            validation_result=result.get("validation_result"),
            calculation_result=result.get("calculation_result")
        )
    except Exception as e:
        # Wrap the exception in custom MechMind exception with stack trace details
        custom_error = MechMind(error_message=str(e), error_detail=sys)
        logger.error(f"Error processing query: {custom_error.error_message}")
        
        raise HTTPException(status_code=500, detail=custom_error.error_message)
