from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from core.models.cricket_match_winner_details import CricketMatchWinnerDetails
from core.models.cricket_event import CricketEvent
from core.models.cricket_match_details import CricketMatchDetails
from core.models.cricket_team import CricketTeam
from core.models.cricket_player import CricketPlayer


class CricketEventResource(resources.ModelResource):

    class Meta:
        model = CricketEvent

        # Fields to import/export
        fields = (
            "event_id",
            "display_event_id",
            "event_name",
            "short_name",
            "logo_url",
            "organizer",
            "location",
            "status",
            "start_date",
            "end_date",
            "is_public",
            "allow_predictions",
            "is_featured",
        )

        # Unique key for update vs create
        import_id_fields = ("event_id",)

        # Maintain order in export
        export_order = fields

        # Optional improvements
        skip_unchanged = True
        report_skipped = True

    def get_instance(self, instance_loader, row):
        # Try UUID first
        event_id = row.get("event_id")
        if event_id:
            try:
                return CricketEvent.objects.get(event_id=event_id)
            except CricketEvent.DoesNotExist:
                pass

        # fallback to display_event_id
        return super().get_instance(instance_loader, row)


class CricketPlayerResource(resources.ModelResource):

    # ---------- FOREIGN KEYS ----------

    event = fields.Field(
        column_name="event",
        attribute="event",
        widget=ForeignKeyWidget(CricketEvent, "display_event_id")
    )

    team = fields.Field(
        column_name="team",
        attribute="team",
        widget=ForeignKeyWidget(CricketTeam, "team_id")  # UUID FK ✅
    )

    class Meta:
        model = CricketPlayer

        fields = (
            "player_id",  # ✅ REQUIRED
            "display_player_id",
            "player_name",
            "short_name",
            "role",
            "event",
            "team",
            "batting_style",
            "bowling_style",
                        # "playing_status",
            # "playing11_status",
            "is_active",
            "is_deleted",
        )

        # ✅ SWITCH TO UUID IMPORT
        import_id_fields = ("player_id",)

        export_order = fields

        skip_unchanged = True
        report_skipped = True

    # ✅ DO NOT REMOVE UUID
    def before_import_row(self, row, **kwargs):

        if not row.get("player_id"):
            raise ValueError("player_id is required for UUID import")

        if not row.get("player_name"):
            raise ValueError("player_name is required")

    # ✅ UUID MATCHING
    def get_instance(self, instance_loader, row):
        player_id = row.get("player_id")

        if player_id:
            try:
                return CricketPlayer.objects.get(player_id=player_id)
            except CricketPlayer.DoesNotExist:
                return None  # create new

        return None


class CricketTeamResource(resources.ModelResource):

    # ---------- FOREIGN KEY ----------

    event = fields.Field(
        column_name="event",
        attribute="event",
        widget=ForeignKeyWidget(CricketEvent, "display_event_id")
    )

    class Meta:
        model = CricketTeam

        fields = (
            "team_id",   # ✅ REQUIRED for import
            "display_team_id",
            "team_name",
            "short_name",
            "location",
            "home_stadium",
            "event",
            "is_active",
            "is_featured",
        )

        # ✅ UUID-based import
        import_id_fields = ("team_id",)

        export_order = fields

        skip_unchanged = True
        report_skipped = True

    # ✅ VALIDATION (do NOT remove team_id)
    def before_import_row(self, row, **kwargs):

        if not row.get("team_id"):
            raise ValueError("team_id is required for UUID-based import")

        if not row.get("team_name"):
            raise ValueError("team_name is required")

    # ✅ ensure UUID matching works properly
    def get_instance(self, instance_loader, row):
        team_id = row.get("team_id")

        if team_id:
            try:
                return CricketTeam.objects.get(team_id=team_id)
            except CricketTeam.DoesNotExist:
                return None  # create new

        return None


class CricketMatchDetailsResource(resources.ModelResource):

    # ---------- FOREIGN KEYS (UUID BASED) ----------

    event = fields.Field(
        column_name="event",
        attribute="event",
        widget=ForeignKeyWidget(CricketEvent, "display_event_id")  # OK to keep
    )

    team1 = fields.Field(
        column_name="team1",
        attribute="team1",
        widget=ForeignKeyWidget(CricketTeam, "team_id")  # ✅ UUID
    )

    team2 = fields.Field(
        column_name="team2",
        attribute="team2",
        widget=ForeignKeyWidget(CricketTeam, "team_id")  # ✅ UUID
    )

    class Meta:
        model = CricketMatchDetails

        fields = (
            "match_id",   # ✅ UUID (PRIMARY IMPORT KEY)
            "display_match_id",
            "event",
            "team1",
            "team2",
            "match_date",
            "match_time",
            "match_type",
            "status_id",
            "location",
            "stadium",
            "match_name1",
            "match_name2",
            "is_active",
            "is_featured",
            "is_deleted",
            "allow_predictions",
        )

        # ✅ UUID-based import
        import_id_fields = ("match_id",)

        export_order = fields

        skip_unchanged = True
        report_skipped = True

    # ✅ VALIDATION (DO NOT REMOVE UUID)
    def before_import_row(self, row, **kwargs):

        if not row.get("match_id"):
            raise ValueError("match_id is required")

        if not row.get("team1"):
            raise ValueError("team1 (team_id) is required")

        if not row.get("team2"):
            raise ValueError("team2 (team_id) is required")

    # ✅ MATCH INSTANCE USING UUID
    def get_instance(self, instance_loader, row):
        match_id = row.get("match_id")

        if match_id:
            try:
                return CricketMatchDetails.objects.get(match_id=match_id)
            except CricketMatchDetails.DoesNotExist:
                return None  # create new

        return None

# class CricketMatchWinnerDetailsResource(resources.ModelResource):

#     # ---------- FOREIGN KEYS (UUID BASED) ----------

#     event = fields.Field(
#         column_name="event",
#         attribute="event",
#         widget=ForeignKeyWidget(CricketEvent, "display_event_id")  # OK
#     )

#     match = fields.Field(
#         column_name="match",
#         attribute="match",
#         widget=ForeignKeyWidget(CricketMatchDetails, "match_id")  # ✅ UUID
#     )

#     winner_team = fields.Field(
#         column_name="winner_team",
#         attribute="winner_team",
#         widget=ForeignKeyWidget(CricketTeam, "team_id")  # ✅ UUID
#     )

#     player_of_match = fields.Field(
#         column_name="player_of_match",
#         attribute="player_of_match",
#         widget=ForeignKeyWidget(CricketPlayer, "player_id")  # ✅ UUID
#     )

#     most_runs_player = fields.Field(
#         column_name="most_runs_player",
#         attribute="most_runs_player",
#         widget=ForeignKeyWidget(CricketPlayer, "player_id")  # ✅ UUID
#     )

#     most_wickets_taker = fields.Field(
#         column_name="most_wickets_taker",
#         attribute="most_wickets_taker",
#         widget=ForeignKeyWidget(CricketPlayer, "player_id")  # ✅ UUID
#     )

#     class Meta:
#         model = CricketMatchWinnerDetails

#         fields = (
#             "winner_id",   # ✅ UUID
#             "event",
#             "match",
#             "winner_team",
#             "player_of_match",
#             "most_runs_player",
#             "most_wickets_taker",
#         )

#         # ✅ PRIMARY KEY IMPORT
#         import_id_fields = ("winner_id",)

#         export_order = fields

#         skip_unchanged = True
#         report_skipped = True

#     # ✅ VALIDATION
#     def before_import_row(self, row, **kwargs):

#         if not row.get("winner_id"):
#             raise ValueError("winner_id is required")

#         if not row.get("match"):
#             raise ValueError("match_id is required")


from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

class CricketMatchWinnerDetailsResource(resources.ModelResource):

    # ---------- FOREIGN KEYS ----------
    event = fields.Field(
        column_name="event",
        attribute="event",
        widget=ForeignKeyWidget(CricketEvent, "display_event_id")
    )

    match = fields.Field(
        column_name="match",
        attribute="match",
        widget=ForeignKeyWidget(CricketMatchDetails, "match_id")
    )

    winner_team = fields.Field(
        column_name="winner_team",
        attribute="winner_team",
        widget=ForeignKeyWidget(CricketTeam, "team_id")
    )

    # ---------- MANY TO MANY ----------
    player_of_match_1 = fields.Field(
        column_name="player_of_match",
        attribute="player_of_match_1",
        widget=ManyToManyWidget(CricketPlayer, field="player_id", separator=",")
    )

    most_runs_player_1 = fields.Field(
        column_name="most_runs_player",
        attribute="most_runs_player_1",
        widget=ManyToManyWidget(CricketPlayer, field="player_id", separator=",")
    )

    most_wickets_player_1 = fields.Field(
        column_name="most_wickets_taker",
        attribute="most_wickets_player_1",
        widget=ManyToManyWidget(CricketPlayer, field="player_id", separator=",")
    )

    class Meta:
        model = CricketMatchWinnerDetails

        fields = (
            "winner_id",
            "event",
            "match",
            "winner_team",
            "player_of_match_1",
            "most_runs_player_1",
            "most_wickets_player_1",
        )

        import_id_fields = ("winner_id",)
        export_order = fields

        skip_unchanged = True
        report_skipped = True

    # ---------- VALIDATION ----------
    def before_import_row(self, row, **kwargs):

        if not row.get("winner_id"):
            raise ValueError("winner_id is required")

        if not row.get("match"):
            raise ValueError("match_id is required")