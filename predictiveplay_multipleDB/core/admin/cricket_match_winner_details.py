# from django.contrib import admin
# from import_export.admin import ImportExportModelAdmin

# from core.models.cricket_match_winner_details import CricketMatchWinnerDetails
# from core.resources import CricketMatchWinnerDetailsResource

# @admin.register(CricketMatchWinnerDetails)
# class CricketMatchWinnerDetailsAdmin(ImportExportModelAdmin):
#     resource_class = CricketMatchWinnerDetailsResource

#     # ---------- LIST VIEW ----------
#     list_display = (
#         "match",
#         "event",
#         "winner_team",
#         "get_player_of_match",
#         "get_most_runs_players",
#         "get_most_wickets_players",
#     )

#     list_filter = (
#         "event",
#         "winner_team",
#     )

#     search_fields = (
#         "match__match_name2",
#         "winner_team__team_name",
#         "player_of_match__player_name",
#         "most_runs_player__player_name",
#         "most_wickets_taker__player_name",
#     )

#     ordering = (
#         "event",
#         "match",
#     )

#     # ---------- READ-ONLY ----------
#     readonly_fields = (
#         "winner_id",
#         "created_at",
#         "updated_at",
#     )

#     # ---------- FORM LAYOUT ----------
#     fieldsets = (
#         ("Match Mapping", {
#             "fields": (
#                 "event",
#                 "match",
#             )
#         }),
#         ("Winner & Awards", {
#             "fields": (
#                 "winner_team",
#                 "player_of_match",
#                 "most_runs_player",
#                 "most_wickets_taker",
#             )
#         }),
#         ("Audit", {
#             "fields": (
#                 "winner_id",
#                 "created_at",
#                 "updated_at",
#             )
#         }),
#     )

#     # ---------- SAFETY ----------
#     def has_delete_permission(self, request, obj=None):
#         return False

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from core.models.cricket_match_winner_details import CricketMatchWinnerDetails
from core.resources import CricketMatchWinnerDetailsResource


@admin.register(CricketMatchWinnerDetails)
class CricketMatchWinnerDetailsAdmin(ImportExportModelAdmin):
    resource_class = CricketMatchWinnerDetailsResource

    # ---------- LIST VIEW ----------
    list_display = (
        "match",
        "event",
        "winner_team",
        "get_player_of_match",
        "get_most_runs_players",
        "get_most_wickets_players",
    )

    list_filter = (
        "event",
        "winner_team",
    )

    # ✅ FIXED: Use M2M fields
    search_fields = (
        "match__match_name2",
        "winner_team__team_name",
        "player_of_match_1__player_name",
        "most_runs_player_1__player_name",
        "most_wickets_player_1__player_name",
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
                "player_of_match_1",
                "most_runs_player_1",
                "most_wickets_player_1",
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

    # ---------- CUSTOM DISPLAY METHODS ----------
    def get_player_of_match(self, obj):
        return ", ".join([p.player_name for p in obj.player_of_match_1.all()])
    get_player_of_match.short_description = "Player of Match"

    def get_most_runs_players(self, obj):
        return ", ".join([p.player_name for p in obj.most_runs_player_1.all()])
    get_most_runs_players.short_description = "Most Runs"

    def get_most_wickets_players(self, obj):
        return ", ".join([p.player_name for p in obj.most_wickets_player_1.all()])
    get_most_wickets_players.short_description = "Most Wickets"

    # ---------- SAFETY ----------
    def has_delete_permission(self, request, obj=None):
        return False