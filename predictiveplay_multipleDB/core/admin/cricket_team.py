from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from core.resources import CricketTeamResource
from core.models.cricket_team import CricketTeam

@admin.register(CricketTeam)
class CricketTeamAdmin(ImportExportModelAdmin):
    resource_class = CricketTeamResource

    list_display = (
        "short_name",
        "team_name",
        "event",
        "display_team_id",
        "is_active",
    )

    list_filter = (
        "event",
        "is_active",
    )

    search_fields = (
        "team_name",
        "short_name",
    )

    ordering = ("event", "display_team_id")

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Team Info", {
            "fields": (
                "display_team_id",
                "team_name",
                "short_name",
                "logo_url",
            )
        }),
        ("Event Mapping", {
            "fields": ("event",)
        }),
        ("Status", {
            "fields": (
                "is_active",
                "is_featured",
            )
        }),
        ("Audit", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )
