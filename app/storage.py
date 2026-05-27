from typing import Optional, List, Dict, Any

class TaskStorage:
    def __init__(self):
        self._tasks: Dict[int, Dict[str, Any]] = {}
        self._counter: int = 1

    def create(self, task_data: dict) -> dict:
        task_id = self._counter
        self._counter += 1
        task = {"id": task_id, **task_data}
        self._tasks[task_id] = task
        return task

    def get(self, task_id: int) -> Optional[dict]:
        return self._tasks.get(task_id)

    def get_all_by_owner(self, owner_id: int, status: Optional[str] = None, min_priority: Optional[int] = None) -> List[dict]:
        tasks = [t for t in self._tasks.values() if t["owner_id"] == owner_id]
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        if min_priority is not None:
            tasks = [t for t in tasks if t["priority"] >= min_priority]
        return tasks

    def update_status(self, task_id: int, status: str) -> Optional[dict]:
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = status
            return self._tasks[task_id]
        return None

    def delete(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def clear(self):
        self._tasks.clear()
        self._counter = 1

_storage = TaskStorage()

def get_storage() -> TaskStorage:
    return _storage