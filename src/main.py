from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from src.api.endpoint import router as api_router

app = FastAPI(
    title="Engineering Agent API",
    description="API for the LangGraph Engineering Workflow",
    version="1.0.0"
)

# Include the API router
app.include_router(api_router, prefix="/api/v1")

frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def root():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to the Engineering Agent API! Visit /docs for the Swagger UI."}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
