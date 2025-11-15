"""
ADHD-Friendly Dev Dashboard - Backend
FastAPI server with WebSocket support
"""

from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json


# Models
class Task(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    priority: int = 1  # 1-5
    energy_required: int = 5  # 1-10
    estimated_minutes: int = 25
    completed: bool = False
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    xp_reward: int = 10


class PomodoroSession(BaseModel):
    id: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: int = 25
    type: str = "work"  # work, short_break, long_break
    completed: bool = False
    task_id: Optional[int] = None


class EnergyLog(BaseModel):
    id: Optional[int] = None
    timestamp: datetime
    energy_level: int  # 1-10
    focus_level: int  # 1-10
    mood: str  # happy, neutral, stressed, tired
    notes: Optional[str] = None


class UserStats(BaseModel):
    total_xp: int = 0
    level: int = 1
    current_streak: int = 0
    longest_streak: int = 0
    total_tasks: int = 0
    total_pomodoros: int = 0
    achievements: List[str] = []


# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


# Pomodoro Timer State
class PomodoroTimer:
    def __init__(self):
        self.is_running = False
        self.current_duration = 25
        self.time_remaining = 25 * 60
        self.start_time = None
        self.task_id = None

    async def start(self, duration: int = 25, task_id: Optional[int] = None):
        self.is_running = True
        self.current_duration = duration
        self.time_remaining = duration * 60
        self.start_time = datetime.now()
        self.task_id = task_id

        # Start countdown
        asyncio.create_task(self.countdown())

    async def countdown(self):
        while self.is_running and self.time_remaining > 0:
            await asyncio.sleep(1)
            self.time_remaining -= 1

            # Broadcast time remaining every 10 seconds
            if self.time_remaining % 10 == 0:
                await manager.broadcast({
                    "type": "pomodoro_tick",
                    "time_remaining": self.time_remaining,
                    "percentage": (self.time_remaining / (self.current_duration * 60)) * 100
                })

        if self.time_remaining == 0:
            await self.complete()

    async def complete(self):
        self.is_running = False
        await manager.broadcast({
            "type": "pomodoro_complete",
            "duration": self.current_duration,
            "xp_earned": 5
        })

    def pause(self):
        self.is_running = False

    def stop(self):
        self.is_running = False
        self.time_remaining = 0


pomodoro_timer = PomodoroTimer()


# App initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 ADHD Dev Dashboard starting...")
    yield
    # Shutdown
    print("👋 ADHD Dev Dashboard shutting down...")


app = FastAPI(
    title="ADHD Dev Dashboard API",
    description="Visual task tracking with dopamine-driven gamification",
    version="0.1.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory storage (replace with SQLite in production)
tasks_db: List[Task] = []
pomodoros_db: List[PomodoroSession] = []
energy_logs_db: List[EnergyLog] = []
user_stats = UserStats()


# Routes
@app.get("/")
async def root():
    return {
        "message": "ADHD Dev Dashboard API",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


# Tasks endpoints
@app.post("/api/tasks", response_model=Task)
async def create_task(task: Task):
    task.id = len(tasks_db) + 1
    task.created_at = datetime.now()
    tasks_db.append(task)

    await manager.broadcast({
        "type": "task_created",
        "task": task.dict()
    })

    return task


@app.get("/api/tasks", response_model=List[Task])
async def get_tasks(completed: Optional[bool] = None):
    if completed is None:
        return tasks_db
    return [t for t in tasks_db if t.completed == completed]


@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: Task):
    for i, task in enumerate(tasks_db):
        if task.id == task_id:
            task_update.id = task_id
            tasks_db[i] = task_update
            await manager.broadcast({
                "type": "task_updated",
                "task": task_update.dict()
            })
            return task_update

    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/api/tasks/{task_id}/complete")
async def complete_task(task_id: int):
    for task in tasks_db:
        if task.id == task_id:
            task.completed = True
            task.completed_at = datetime.now()

            # Award XP
            user_stats.total_xp += task.xp_reward
            user_stats.total_tasks += 1
            user_stats.level = calculate_level(user_stats.total_xp)

            await manager.broadcast({
                "type": "task_completed",
                "task": task.dict(),
                "xp_earned": task.xp_reward,
                "new_level": user_stats.level
            })

            return {
                "task": task,
                "xp_earned": task.xp_reward,
                "total_xp": user_stats.total_xp,
                "level": user_stats.level
            }

    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int):
    global tasks_db
    tasks_db = [t for t in tasks_db if t.id != task_id]
    await manager.broadcast({
        "type": "task_deleted",
        "task_id": task_id
    })
    return {"status": "deleted"}


# Pomodoro endpoints
@app.post("/api/pomodoro/start")
async def start_pomodoro(duration: int = 25, task_id: Optional[int] = None):
    if pomodoro_timer.is_running:
        raise HTTPException(status_code=400, detail="Pomodoro already running")

    await pomodoro_timer.start(duration, task_id)

    return {
        "status": "started",
        "duration": duration,
        "task_id": task_id
    }


@app.post("/api/pomodoro/pause")
async def pause_pomodoro():
    pomodoro_timer.pause()
    return {"status": "paused"}


@app.post("/api/pomodoro/stop")
async def stop_pomodoro():
    pomodoro_timer.stop()
    return {"status": "stopped"}


@app.get("/api/pomodoro/status")
async def pomodoro_status():
    return {
        "is_running": pomodoro_timer.is_running,
        "time_remaining": pomodoro_timer.time_remaining,
        "duration": pomodoro_timer.current_duration,
        "task_id": pomodoro_timer.task_id
    }


@app.get("/api/pomodoro/stats")
async def pomodoro_stats():
    today = datetime.now().date()
    today_sessions = [p for p in pomodoros_db if p.start_time.date() == today]

    return {
        "today": len(today_sessions),
        "total": len(pomodoros_db),
        "completed": len([p for p in pomodoros_db if p.completed])
    }


# Energy tracking
@app.post("/api/energy", response_model=EnergyLog)
async def log_energy(energy: EnergyLog):
    energy.id = len(energy_logs_db) + 1
    energy.timestamp = datetime.now()
    energy_logs_db.append(energy)

    await manager.broadcast({
        "type": "energy_logged",
        "energy": energy.dict()
    })

    return energy


@app.get("/api/energy/today", response_model=List[EnergyLog])
async def get_today_energy():
    today = datetime.now().date()
    return [e for e in energy_logs_db if e.timestamp.date() == today]


@app.get("/api/energy/insights")
async def energy_insights():
    if len(energy_logs_db) < 7:
        return {"message": "Need at least 7 days of data for insights"}

    # Simple insights
    avg_energy = sum(e.energy_level for e in energy_logs_db) / len(energy_logs_db)
    avg_focus = sum(e.focus_level for e in energy_logs_db) / len(energy_logs_db)

    return {
        "avg_energy": round(avg_energy, 1),
        "avg_focus": round(avg_focus, 1),
        "best_time": "Morning (9-11am)",  # Placeholder - implement actual analysis
        "recommendation": "Your focus peaks in the morning. Schedule deep work then!"
    }


# User stats
@app.get("/api/stats", response_model=UserStats)
async def get_stats():
    return user_stats


# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Helper functions
def calculate_level(xp: int) -> int:
    """Calculate level from XP (simple formula)"""
    if xp < 500:
        return 1 + xp // 100
    elif xp < 1500:
        return 5 + (xp - 500) // 200
    elif xp < 5000:
        return 10 + (xp - 1500) // 350
    else:
        return 20 + (xp - 5000) // 500


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
