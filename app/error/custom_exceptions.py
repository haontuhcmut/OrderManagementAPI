from fastapi import HTTPException, status

class NotFound(HTTPException):
    def __init__(self, entity: str):
        super.__init__(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "Error not found", "message": f"{entity} not found"})
