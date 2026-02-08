from django.contrib import admin
from core.models.cricket_match_winner_details import CricketMatchWinnerDetails


@admin.register(CricketMatchWinnerDetails)
class CricketMatchWinnerDetailsAdmin(admin.ModelAdmin):
    """
    Admin configuration for CricketMatchWinnerDetails
    """

    # ---------- LIST VIEW ----------
    list_display = (
        "event",
        "match",
        "winner_team",
        "player_of_match",
        "most_runs_player",
        "most_wickets_taker",
        "created_at",
    )

    list_filter = (
        "event",
        "winner_team",
    )

    search_fields = (
        "match__match_name2",
        "winner_team__team_name",
        "player_of_match__player_name",
        "most_runs_player__player_name",
        "most_wickets_taker__player_name",
    )

    ordering = (
        "event",
        "match",
    )

    # ---------- READ-ONLY ----------
    readonly_fields = (
        "winner_id",
        "created_at",
        "updated_at",
    )

    # ---------- FORM LAYOUT ----------
    fieldsets = (
        ("Match Mapping", {
            "fields": (
                "event",
                "match",
            )
        }),
        ("Winner & Awards", {
            "fields": (
                "winner_team",
                "player_of_match",
                "most_runs_player",
                "most_wickets_taker",
            )
        }),
        ("Audit", {
            "fields": (
                "winner_id",
                "created_at",
                "updated_at",
            )
        }),
    )

    # ---------- SAFETY ----------
    def has_delete_permission(self, request, obj=None):
        """
        Prevent accidental deletion of match results.
        """
    