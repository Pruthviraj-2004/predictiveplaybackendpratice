from django.contrib import admin
from core.models.company import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Admin configuration for Company.
    Safe with automatic DB creation logic.
    """

    # ---------- LIST VIEW ----------

    list_display = (
        "company_name",
        "company_display_id",
        "company_domain",
        "db_alias",
        "is_active",
        "db_created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "company_name",
        "company_domain",
        "company_display_id",
    )

    ordering = ("company_name",)

    # ---------- READ-ONLY FIELDS ----------
    # These should NEVER be edited manually

    readonly_fields = (
        "company_id",
        "company_display_id",
        "db_alias",
        "db_created_at",
    )

    # ---------- FORM LAYOUT ----------

    fieldsets = (
        ("Company Information", {
            "fields": (
                "company_name",
                "company_domain",
            )
        }),
        ("Database Mapping (Auto-generated)", {
            "fields": (
                "company_display_id",
                "db_alias",
                "db_created_at",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
            )
        }),
        ("Internal IDs", {
            "fields": (
                "company_id",
            )
        }),
    )

    # ---------- SAFETY GUARDS ----------

    def has_delete_permission(self, request, obj=None):
        """
        Prevent accidental deletion of companies.
        DBs are not auto-dropped.
        """
        return False
