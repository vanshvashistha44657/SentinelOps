from fastapi import HTTPException, status

class SentinelOpsException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class EntityNotFoundException(SentinelOpsException):
    def __init__(self, entity: str, id: str):
        super().__init__(f"{entity} with ID {id} not found", status.HTTP_404_NOT_FOUND)

class AuthenticationException(SentinelOpsException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)

class PermissionDeniedException(SentinelOpsException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(detail, status.HTTP_403_FORBIDDEN)
