from enum import Enum  

class USER_EVENTS(Enum):

    CREATED = "user.created"
    UPDATED = "user.updated"
    DELETED = "user.deleted"