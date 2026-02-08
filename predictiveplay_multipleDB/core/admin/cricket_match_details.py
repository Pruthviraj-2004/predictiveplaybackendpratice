from django.contrib import admin
from core.models.cricket_match_details import CricketMatchDetails


@admin.register(CricketMatchDetails)
class CricketMatchDetailsAdmin(admin.ModelAdmin):
    """
    Admin configuration for CricketMatchDetails
    """

    # ---------- LIST PAGE ----------

    list_display = (
        "display_match_id",
        "event",
        "match_date",
        "match_time",
        "match_name2",
        "status_id",
        "is_active",
        "allow_predictions",
    )

    list_filter = (
        "event",
        "status_id",
        "is_active",
        "allow_predictions",
        "is_featured",
        "is_deleted",
    )

    search_fields = (
        "match_name1",
        "match_name2",
        "stadium",
        "location",
    )

    ordering = (
        "event",
        "display_match_id",
    )

    # ---------- READ ONLY ----------

    readonly_fields = (
        "match_id",
        "created_at",
        "updated_at",
    )

    # ---------- FORM LAYOUT ----------

    fieldsets = (
        ("Match Identity", {
            "fields": (
                "display_match_id",
                "event",
            )
        }),
        ("Teams", {
            "fields": (
                "team1",
                "team2",
            )
        }),
        ("Schedule", {
            "fields": (
                "match_date",
                "match_time",
                "match_type",
            )
        }),
        ("Match Status", {
            "fields": (
                "status_id",
                "allow_predictions",
            )
        }),
        ("Venue", {
            "fields": (
                "location",
                "stadium",
            )
        }),
        ("Display Names", {
            "fields": (
                "match_name1",
                "match_name2",
            )
        }),
        ("Flags", {
            "fields": (
                "is_active",
                "is_featured",
                "is_deleted",
            )
        }),
        ("Audit", {
            "fields": (
                "match_id",
                "created_at",
                "updated_at",
            )
        }),
    )

    # ---------- ADMIN SAFETY ----------

    def get_queryset(self, request):
        """
        Default admin view hides deleted matches.
        """
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False)
