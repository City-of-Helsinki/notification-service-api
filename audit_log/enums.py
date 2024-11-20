from enum import Enum

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class Operation(TextChoices):
    CREATE = "CREATE", _("Create")
    READ = "READ", _("Read")
    UPDATE = "UPDATE", _("Update")
    DELETE = "DELETE", _("Delete")


class Role(TextChoices):
    OWNER = "OWNER", _("Owner")
    USER = "USER", _("User")
    SYSTEM = "SYSTEM", _("System")
    ANONYMOUS = "ANONYMOUS", _("Anonymous")
    ADMIN = "ADMIN", _("Admin")


class Status(TextChoices):
    SUCCESS = "SUCCESS", _("Success")
    FORBIDDEN = "FORBIDDEN", _("Forbidden")


class StoreObjectState(Enum):
    # Do not store object state
    NONE = "none"
    # Store only the old object state
    OLD_ONLY = "old-only"
    # Store only the new object state
    NEW_ONLY = "new-only"
    # Store the old and the new object states
    OLD_AND_NEW_BOTH = "old-and-new"
    # Store only diff
    DIFF = "diff"
    # Store the old and the new object states and also the diff
    ALL = "all"
