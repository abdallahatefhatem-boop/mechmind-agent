from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Any, Optional
import sys
import asyncio
import uuid
import json
from src.pipeline.graph import run_workflow, workflow
from langchain_core.messages import HumanMessage
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

@router.get("/ask/stream")
async def ask_engineering_question_stream(query: str, thread_id: Optional[str] = None):
    t_id = thread_id or str(uuid.uuid4())
    config = {
        "recursion_limit": 25,
        "configurable": {"thread_id": t_id}
    }
    
    q = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def run_sync_stream():
        try:
            for event in workflow.stream(
                {"messages": [HumanMessage(content=query)], "user_query": query},
                config=config,
                stream_mode="updates"
            ):
                asyncio.run_coroutine_threadsafe(q.put(event), loop)
            asyncio.run_coroutine_threadsafe(q.put(None), loop)
        except Exception as exc:
            asyncio.run_coroutine_threadsafe(q.put(exc), loop)

    async def event_generator():
        yield f"data: {json.dumps({'event': 'start', 'thread_id': t_id})}\n\n"
        
        asyncio.create_task(asyncio.to_thread(run_sync_stream))
        
        while True:
            event = await q.get()
            if event is None:
                break
            if isinstance(event, Exception):
                import traceback
                traceback.print_exception(type(event), event, event.__traceback__)
                yield f"data: {json.dumps({'event': 'error', 'message': str(event)})}\n\n"
                break
                
            for node_name, state in event.items():
                yield f"data: {json.dumps({'event': 'node', 'node': node_name})}\n\n"
                if node_name in ["format_output_node", "general_chat_node"]:
                    yield f"data: {json.dumps({'event': 'result', 'data': {'explanation': state.get('explanation'), 'selected_tool': state.get('selected_tool'), 'calculation_result': state.get('calculation_result')}})}\n\n"
            
        yield f"data: {json.dumps({'event': 'end'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")