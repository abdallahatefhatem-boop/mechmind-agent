import asyncio
import json
import sys
import uuid
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from src.Exceptions import MechMind
from src.Logger import logging
from src.pipeline.graph import run_workflow, workflow

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    thread_id: Optional[str] = Field(
        default=None, 
        description="Unique session/thread ID to persist conversation state across requests"
    )


class QueryResponse(BaseModel):
    thread_id: str
    explanation: str
    selected_tool: Optional[list[str]] = None
    validation_result: Optional[Any] = None
    calculation_result: Optional[Any] = None


@router.post("/ask", response_model=QueryResponse)
async def ask_engineering_question(request: QueryRequest):
    # Maintain existing thread_id or generate a new UUID for new sessions
    thread_id = request.thread_id or str(uuid.uuid4())
    
    try:
        logging.info(f"Received query: {request.query} (thread_id: {thread_id})")
        
        # Run synchronous workflow in a worker thread to avoid blocking the FastAPI event loop
        result = await asyncio.to_thread(
            run_workflow, 
            query=request.query, 
            thread_id=thread_id
        )
        
        logging.info(f"Successfully processed query for thread_id: {thread_id}")
        
        return QueryResponse(
            thread_id=thread_id,
            explanation=result.get("explanation", ""),
            selected_tool=result.get("selected_tool"),
            validation_result=result.get("validation_result"),
            calculation_result=result.get("calculation_result")
        )
        
    except Exception as e:
        custom_error = MechMind(error_message=str(e), error_detail=sys)
        logging.error(f"Error processing query for thread_id {thread_id}: {custom_error.error_message}")
        
        # Return structured response instead of raising an uncaught HTTP 500 exception
        return QueryResponse(
            thread_id=thread_id,
            explanation=f"Execution Error: {str(e)}. Please check your calculation inputs and try again.",
            selected_tool=None,
            validation_result={"status": "error", "error_message": str(e)},
            calculation_result=None
        )