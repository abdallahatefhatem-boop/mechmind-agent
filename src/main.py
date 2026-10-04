from fastapi import FastAPI
import uvicorn
from src.api.endpoint import router as api_router

app = FastAPI(
    title="Engineering Agent API",
    description="API for the LangGraph Engineering Workflow",
    version="1.0.0"
)

# Include the API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the Engineering Agent API! Visit /docs for the Swagger UI."}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
