from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
from pathlib import Path
import copy

# class Command(BaseCommand):
#     help = "Create a new company SQLite database and run migrations"

#     def add_arguments(self, parser):
#         parser.add_argument("company", type=str)

#     def handle(self, *args, **options):
#         company = options["company"].lower()
#         db_alias = f"{company}_db"
#         db_file = f"{db_alias}.sqlite3"
#         db_path = Path(settings.BASE_DIR) / db_file

#         if db_path.exists():
#             self.stdout.write(self.style.WARNING("DB already exists"))
#             return

#         default_db = settings.DATABASES["default"]

#         settings.DATABASES[db_alias] = {
#             **copy.deepcopy(default_db),
#             "NAME": db_path,
#         }

#         call_command("migrate", database=db_alias)

#         self.stdout.write(
#             self.style.SUCCESS(f"Created database: {db_file}")
#         )

from core.db_utils import create_company_database

class Command(BaseCommand):
    help = "Create a new company database"

    def add_arguments(self, parser):
        parser.add_argument("db_alias", type=str)

    def handle(self, *args, **options):
        db_alias = options["db_alias"]
        create_company_database(db_alias)
        self.stdout.write(self.style.SUCCESS(f"Database ready: {db_alias}"))