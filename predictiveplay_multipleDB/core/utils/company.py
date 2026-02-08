# from core.models import Company


# def get_company_db(company_display_id):
#     """
#     Resolve company DB alias from default DB.
#     """
#     try:
#         company = Company.objects.using("default").get(
#             company_display_id=company_display_id,
#             is_active=True,
#         )
#     except Company.DoesNotExist:
#         return None

#     return company.db_alias

# core/utils/company.py

from core.models import Company
from core.db_utils import create_company_database


def get_company_db(company_display_id):
    """
    Resolve and ensure company DB exists.
    """
    try:
        company = Company.objects.using("default").get(
            company_display_id=company_display_id,
            is_active=True,
        )
    except Company.DoesNotExist:
        return None

    # ✅ Ensure DB is registered + migrated
    create_company_database(company.db_alias)

    return company.db_alias
