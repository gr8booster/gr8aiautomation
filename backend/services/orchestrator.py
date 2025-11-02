"""
Custom AI-optimized orchestrator service
DB-backed state machine for workflow execution
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from enum import Enum

class NodeType(Enum):
    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    AI = "ai"

class OrchestratorService:
    def __init__(self, db):
        self.db = db
        self.executions = db["executions"]
    
    async def create_execution(self, workflow_id: str, triggered_by: str = "manual") -> str:
        """Create a new execution"""
        execution_id = str(uuid.uuid4())
        
        execution = {
            "_id": execution_id,
            "workflow_id": workflow_id,
            "triggered_by": triggered_by,
            "state": "pending",
            "started_at": datetime.now(timezone.utc),
            "finished_at": None,
            "logs": [],
            "metrics": {},
            "error": None
        }
        
        await self.executions.insert_one(execution)
        return execution_id
    
    async def update_execution_state(self, execution_id: str, state: str, error: str = None):
        """Update execution state"""
        update = {
            "state": state,
            "updated_at": datetime.now(timezone.utc)
        }
        
        if state in ["completed", "failed"]:
            update["finished_at"] = datetime.now(timezone.utc)
        
        if error:
            update["error"] = error
        
        await self.executions.update_one(
            {"_id": execution_id},
            {"$set": update}
        )
    
    async def add_log(self, execution_id: str, message: str):
        """Add log entry to execution"""
        await self.executions.update_one(
            {"_id": execution_id},
            {"$push": {"logs": f"[{datetime.now(timezone.utc).isoformat()}] {message}"}}
        )
    
    async def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """Get execution details"""
        return await self.executions.find_one({"_id": execution_id})
    
    async def get_executions_for_workflow(self, workflow_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get executions for a workflow"""
        cursor = self.executions.find({"workflow_id": workflow_id}).sort("started_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get orchestrator queue stats"""
        pending_count = await self.executions.count_documents({"state": "pending"})
        running_count = await self.executions.count_documents({"state": "running"})
        
        return {
            "queue_depth": pending_count,
            "running": running_count,
            "healthy": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
