from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

import re



class DataBaseErrorHandler:
    @staticmethod #Do not create instance
    async def handler_integrity_error(e: IntegrityError, session: AsyncSession, entity_name: str):
        await session.rollback()
        if "1062" in str(e.orig): #Duplicate entry error
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "IntegrityError",
                    "message": f"The {entity_name} already exists.",
                    "hint": "Please choose a different name"
                }
            )
        if "1452" in str(e.orig): #Foreign key constraint fails
            match = re.search(r"FOREIGN KEY \(`(.+?)`\)", str(e.orig)) #Search error
            column_name = match.group(1) if match else "Unknown column"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "IntegrityError",
                    "message": f"Foreign key constraint failed for column '{column_name}'.",
                    "hint": "Please check the foreign key values and try again"
                }
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity constraint failed. Please check your input and try again.",
        )
