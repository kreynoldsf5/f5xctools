import datetime

class Error(Exception):
    """Base class for other exceptions"""
    pass

class FindError(Error):
    """Raised when Find operation fails"""
    pass

class CreateError(Error):
    """Raised when Create operation fails"""
    pass

class DelError(Error):
    """Raised when Delete operation fails"""
    pass

class RenewError(Error):
    """Raised when Renew operation fails"""
    pass

class SessionError(Error):
    """Raised when Session operation fails"""
    pass

def findExpiry(staleDays: int):
    expiry = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=staleDays)
    return expiry

"""
Do something when errors are raised instead of 'pass'
"""