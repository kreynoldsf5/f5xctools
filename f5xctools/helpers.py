import datetime

class Error(Exception):
    """Base class for other exceptions"""
    pass

class FindError(Error):
    """Raised when Find operations fail"""
    pass

class DelError(Error):
    """Raised when Delete operations fail"""
    pass

class RenewError(Error):
    """Raised when Renew operations fail"""
    pass

class SessionError(Error):
    """Raised when Session operations fail"""
    pass

def findExpiry(staleDays: int):
    expiry = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=staleDays)
    return expiry