from fastapi import APIRouter, status

router = APIRouter(tags=["health"])


@router.get("/ping", status_code=status.HTTP_200_OK)
async def status():
    """Проверка работоспособности."""
    return {"detail": "pong"}
