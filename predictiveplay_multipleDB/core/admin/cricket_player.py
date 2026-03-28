from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from core.resources import CricketPlayerResource
from core.models.cricket_player import CricketPlayer


@admin.register(CricketPlayer)
class CricketPlayerAdmin(ImportExportModelAdmin):
    resource_class = CricketPlayerResource

    # ---------- LIST VIEW ----------
    list_display = (
        "player_name",
        "team",
        "event",
        "role",
        "is_active",
        "is_deleted",
        "playing_status",
        "playing11_status",
    )

    list_filter = (
        "event",
        "team",
        "role",
        "is_active",
        "is_deleted",
    )

    search_fields = (
        "player_name",
        "short_name",
    )

    ordering = (
        "event",
        "team",
        "display_player_id",
    )

    # ---------- READ-ONLY ----------
    readonly_fields = (
        "player_id",
        "created_at",
        "updated_at",
    )

    # ---------- FORM LAYOUT ----------
    fieldsets = (
        ("Player Info", {
            "fields": (
                "display_player_id",
                "player_name",
                "short_name",
                "role",
            )
        }),
        ("Team & Event", {
            "fields": (
                "event",
                "team",
            )
        }),
        ("Playing Style", {
            "fields": (
                "batting_style",
                "bowling_style",
            )
        }),
        # ("Playing Status", {
        #     "fields": (
        #         "playing_status",
        #         "playing11_status",
        #     )
        # }),
        ("Status", {
            "fields": (
                "is_active",
                "is_deleted",
            )
        }),
        ("Audit", {
            "fields": (
                "player_id",
                "created_at",
                "updated_at",
            )
        }),
    )

    # ---------- SAFETY ----------
    def get_queryset(self, request):
        """
        Hide deleted players by default.
        """
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False)
