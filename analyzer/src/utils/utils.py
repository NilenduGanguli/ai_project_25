import asyncio
import os
from fastapi import HTTPException, UploadFile
import aiofiles


async def _validate_file_async(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )


async def _save_uploaded_file_async(file: UploadFile, file_path: str) -> None:
    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded file: {str(e)}"
        )


async def _cleanup_temp_files_async(temp_file_path: str, temp_dir: str) -> None:
    cleanup_tasks = []

    if await asyncio.to_thread(os.path.exists, temp_file_path):
        cleanup_tasks.append(asyncio.to_thread(os.remove, temp_file_path))

    if await asyncio.to_thread(os.path.exists, temp_dir):
        cleanup_tasks.append(asyncio.to_thread(os.rmdir, temp_dir))

    if cleanup_tasks:
        try:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        except Exception:
            pass
