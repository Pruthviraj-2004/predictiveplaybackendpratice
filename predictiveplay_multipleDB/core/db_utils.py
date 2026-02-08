from django.conf import settings
from django.core.management import call_command
from django.db import connections
from pathlib import Path
import copy


def create_company_database(db_alias: str):
    """
    Create SQLite DB for company and run migrations.
    Safe, complete, Django-compatible.
    """

    # If already registered, do nothing
    if db_alias in connections.databases:
        return

    db_file = f"{db_alias}.sqlite3"
    db_path = Path(settings.BASE_DIR) / db_file

    # ✅ CLONE full default DB config
    base_config = copy.deepcopy(connections.databases["default"])

    # Override only what is different
    base_config["NAME"] = str(db_path)

    # Register
    connections.databases[db_alias] = base_config

    # Ensure DB file exists
    db_path.touch(exist_ok=True)

    # Run migrations
    call_command(
        "migrate",
        database=db_alias,
        interactive=False,
        verbosity=0,
    )
