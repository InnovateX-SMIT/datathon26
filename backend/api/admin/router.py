from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

@router.get("/users")
def get_users_list() -> List[Dict[str, Any]]:
    return [
        {"id": 1, "name": "Officer A", "email": "officer@police.gov.in", "role": "OFFICER"},
        {"id": 2, "name": "Superintendent B", "email": "sp@police.gov.in", "role": "SUPERINTENDENT"},
        {"id": 3, "name": "Admin C", "email": "admin@police.gov.in", "role": "ADMIN"}
    ]

@router.put("/users/{id}/role")
def update_user_role(id: int, role: str) -> Dict[str, Any]:
    return {"id": id, "new_role": role, "status": "updated"}
