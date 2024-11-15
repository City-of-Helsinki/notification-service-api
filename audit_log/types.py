from dataclasses import dataclass
from typing import List, Optional, Union

from audit_log.enums import Operation


@dataclass
class AuditActorData:
    role: str
    uuid: Optional[str]
    ip_address: str

    def __post_init__(self):
        if not isinstance(self.role, str):
            raise TypeError("Role must be a string")
        if not isinstance(self.ip_address, str):
            raise TypeError("Ip_address must be a string")
        if self.uuid and not isinstance(self.uuid, str):
            raise TypeError("Uuid must be a string (or None)")


@dataclass
class AuditTarget:
    path: str
    object_ids: List[str]
    model_name: Optional[str] = None

    def __post_init__(self):
        from audit_log.utils import is_list_of_strings

        if self.model_name and not isinstance(self.model_name, str):
            raise TypeError("Model_name must be a string or None")
        if not isinstance(self.path, str):
            raise TypeError("Path must be a string")
        if not is_list_of_strings(self.object_ids):
            raise TypeError("Object_ids must be a list of strings")


@dataclass
class AuditEvent:
    origin: str
    date_time_epoch: int
    date_time: str
    status: str
    actor: Union[AuditActorData, dict]
    operation: Union[Operation, str]
    target: Union[AuditTarget, dict]

    def __post_init__(self):
        if not isinstance(self.origin, str):
            raise TypeError("Origin must be a string")
        if not isinstance(self.date_time_epoch, int):
            raise TypeError("Date_time_epoch must be an integer")
        if not isinstance(self.date_time, str):
            raise TypeError("Date_time must be a string")
        if not isinstance(self.status, str):
            raise TypeError("Status must be a string")
        if not isinstance(self.actor, (AuditActorData, dict)):
            raise TypeError("Actor must be an AuditActorData instance or a dictionary")
        if isinstance(self.actor, dict):
            self.actor = AuditActorData(
                **self.actor
            )  # Convert dict to dataclass instance
        if not isinstance(self.operation, (Operation, str)):
            raise TypeError("Operation must be an Operation enum value or a string")
        if not isinstance(self.target, (AuditTarget, dict)):
            raise TypeError("Target must be an AuditTarget instance or a dictionary")
        if isinstance(self.target, dict):
            self.target = AuditTarget(
                **self.target
            )  # Convert dict to dataclass instance


@dataclass
class AuditCommitMessage:
    audit_event: Union[AuditEvent, dict]

    def __post_init__(self):
        if not isinstance(self.audit_event, (AuditEvent, dict)):
            raise TypeError(
                "Audit_event must be an AuditEvent instance or a dictionary"
            )
        if isinstance(self.audit_event, dict):
            self.audit_event = AuditEvent(
                **self.audit_event
            )  # Convert dict to dataclass instance
