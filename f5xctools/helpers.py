import datetime

class Error(Exception):
    """Base class for other exceptions"""
    pass

class FindError(Error):
    """Raised when IAM operations fail"""
    pass

class DelError(Error):
    """Raised when IAM operations fail"""
    pass

class RenewError(Error):
    """Raised when IAM operations fail"""
    pass

def findExpiry(staleDays: int):
    expiry = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=staleDays)
    return expiry