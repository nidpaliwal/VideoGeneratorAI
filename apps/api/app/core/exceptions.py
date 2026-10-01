class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "APP_ERROR"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            status_code=404,
            code="NOT_FOUND",
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, status_code=401, code="UNAUTHORIZED")


class ForbiddenError(AppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, status_code=403, code="FORBIDDEN")


class ValidationError(AppException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=422, code="VALIDATION_ERROR")


class RateLimitError(AppException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message=message, status_code=429, code="RATE_LIMITED")


class InsufficientCreditsError(AppException):
    def __init__(self, required: int, available: int):
        super().__init__(
            message=f"Insufficient credits. Required: {required}, Available: {available}",
            status_code=402,
            code="INSUFFICIENT_CREDITS",
        )


class ProviderError(AppException):
    def __init__(self, provider: str, message: str):
        super().__init__(
            message=f"{provider} error: {message}",
            status_code=502,
            code="PROVIDER_ERROR",
        )


class RenderError(AppException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=500, code="RENDER_ERROR")