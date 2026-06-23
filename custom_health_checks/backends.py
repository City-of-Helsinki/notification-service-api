import dataclasses

from django.db import connection, DatabaseError
from health_check.base import HealthCheck
from health_check.exceptions import ServiceUnavailable


@dataclasses.dataclass
class DatabaseHealthCheck(HealthCheck):
    """
    Custom health check for the database connection.
    """

    def run(self):
        """
        Checks the database connection by executing a simple query.
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except DatabaseError as e:
            raise ServiceUnavailable("Database connection failed") from e
