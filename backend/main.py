from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from services.llm_service import TaskPlanningService

app = FastAPI(title="Smart Task Planner API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Make sure this is correct
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class GoalRequest(BaseModel):
    goal: str
    timeline: Optional[str] = None
    priority: Optional[str] = "Medium"

class Task(BaseModel):
    id: int
    description: str
    duration: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    dependencies: List[int] = []

class TaskPlanResponse(BaseModel):
    goal: str
    tasks: List[Task]
    total_duration: str

# Initialize LLM service
llm_service = TaskPlanningService()

@app.get("/")
async def root():
    return {"message": "Smart Task Planner API"}

@app.post("/generate-plan", response_model=TaskPlanResponse)
async def generate_plan(request: GoalRequest):
    try:
        plan = await llm_service.generate_task_plan(request.goal, request.timeline)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plan: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)