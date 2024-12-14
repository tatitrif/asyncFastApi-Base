import os
import uuid

import aiofiles
from fastapi import HTTPException, UploadFile, status

from core.config import BASE_DIR


async def handle_file_upload(
    file: UploadFile,
    dir_location: str = "uploads",
    supported_types: list = None,
    invalid_error_msg: str = "Only .jpeg or .png  files allowed",
) -> str:
    if supported_types is None:
        supported_types = ["image/jpeg", "image/jpg", "image/png"]

    _, ext = os.path.splitext(file.filename)

    if not ext:
        ext = ".jpg"

    dir_location = os.path.join(BASE_DIR, dir_location)

    if not os.path.exists(dir_location):
        os.makedirs(dir_location)

    if file.content_type not in supported_types:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=invalid_error_msg
        )

    file_name = f"{uuid.uuid4().hex}{ext}"

    async with aiofiles.open(os.path.join(dir_location, file_name), "wb") as out_file:
        while content := await file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk

    return file_name
