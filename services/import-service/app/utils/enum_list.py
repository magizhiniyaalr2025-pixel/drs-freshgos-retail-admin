from enum import Enum
class StatusEnum(str, Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    AUTOAPPROVED = "Auto Approved"

    