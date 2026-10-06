# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from typing import Any, Optional
# import sys
# from src.pipeline.graph import run_workflow
# from src.Logger import logging
# from src.Exceptions import MechMind

# router = APIRouter()

# class QueryRequest(BaseModel): # input user question
#     query: str

# class QueryResponse(BaseModel):#  structure output and schema for database
#     explanation: str
#     selected_tool: Optional[list[str]] = None
#     validation_result: Optional[Any] = None
#     calculation_result: Optional[Any] = None

# @router.post("/ask", response_model=QueryResponse)
# async def ask_engineering_question(request: QueryRequest):
#     try:
#         logging.info(f"Received query: {request.query}")
        
#         # Call the langgraph workflow
#         result = run_workflow(request.query)
        
#         logging.info("Successfully processed query.")
        
#         # Map the dictionary returned by run_workflow to our Pydantic model
#         return QueryResponse(
#             explanation=result.get("explanation", ""),
#             selected_tool=result.get("selected_tool"),
#             validation_result=result.get("validation_result"),
#             calculation_result=result.get("calculation_result")
#         )
#     except Exception as e:
#         # Wrap the exception in custom MechMind exception with stack trace details
#         custom_error = MechMind(error_message=str(e), error_detail=sys)
#         logging.error(f"Error processing query: {custom_error.error_message}")
        
#         raise HTTPException(status_code=500, detail=custom_error.error_message)


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Optional
import sys
import asyncio
import uuid
from src.pipeline.graph import run_workflow
from src.Logger import logging
from src.Exceptions import MechMind

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
    try:
        logging.info(f"Received query: {request.query}")
        
        # 1. Use client thread_id or assign a new UUID for new sessions
        thread_id = request.thread_id or str(uuid.uuid4())
        
        # 2. Run synchronous workflow in a worker thread to prevent blocking FastAPI event loop
        result = await asyncio.to_thread(
            run_workflow, 
            query=request.query, 
            thread_id=thread_id
        )
        
        logging.info(f"Successfully processed query for thread_id: {thread_id}")
        
        # 3. Return response including thread_id for subsequent requests
        return QueryResponse(
            thread_id=thread_id,
            explanation=result.get("explanation", ""),
            selected_tool=result.get("selected_tool"),
            validation_result=result.get("validation_result"),
            calculation_result=result.get("calculation_result")
        )
    except Exception as e:
        custom_error = MechMind(error_message=str(e), error_detail=sys)
        logging.error(f"Error processing query: {custom_error.error_message}")
        
        raise HTTPException(status_code=500, detail=custom_error.error_message)