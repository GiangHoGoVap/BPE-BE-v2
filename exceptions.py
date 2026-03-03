class CustomException(Exception):
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.status_code = status_code


class InvalidToken(CustomException):
    def __init__(self, message="Invalid token"):
        super().__init__(message, 401)


class UserNotFound(CustomException):
    def __init__(self, message="User not found"):
        super().__init__(message, 404)


class AccessNotAllowed(CustomException):
    def __init__(self, message="Access not allowed"):
        super().__init__(message, 403)


class WorkspaceNotFound(CustomException):
    def __init__(self, message="Workspace not found"):
        super().__init__(message, 404)


class SurveyNotFound(CustomException):
    def __init__(self, message="Survey not found"):
        super().__init__(message, 404)
