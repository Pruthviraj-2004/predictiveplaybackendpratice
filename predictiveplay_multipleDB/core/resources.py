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
        widget=ForeignKeyWidget(CricketTeam, "team_id")
    )

    class Meta:
        model = CricketPlayer

        # ✅ INCLUDE UUID
        fields = (
            "player_id",
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

        # ✅ business key for import
        import_id_fields = ("display_player_id",)

        export_order = fields

        skip_unchanged = True
        report_skipped = True

    # ✅ Protect UUID
    def before_import_row(self, row, **kwargs):
        row.pop("player_id", None)

        if not row.get("display_player_id"):
            raise ValueError("display_player_id is required")

        if not row.get("player_name"):
            raise ValueError("player_name is required")

    # ✅ Optional UUID fallback
    def get_instance(self, instance_loader, row):
        player_id = row.get("player_id")

        if player_id:
            try:
                return CricketPlayer.objects.get(player_id=player_id)
            except CricketPlayer.DoesNotExist:
                pass

        return super().get_instance(instance_loader, row)


class CricketTeamResource(resources.ModelResource):

    # ---------- FOREIGN KEY ----------

    event = fields.Field(
        column_name="event",
        attribute="event",
        widget=ForeignKeyWidget(CricketEvent, "display_event_id")
    )

    class Meta:
        model = CricketTeam

        # ✅ INCLUDE UUID
        fields = (
            "team_id",
            "display_team_id",
            "team_name",
            "short_name",
            "location",
            "home_stadium",
            "event",
            "is_active",
            "is_featured",
        )

        # ✅ business key
        import_id_fields = ("display_team_id",)

        export_order = fields

        skip_unchanged = True
        report_skipped = True

    # ✅ Protect UUID
    def before_import_row(self, row, **kwargs):
        row.pop("team_id", None)

        if not row.get("display_team_id"):
            raise ValueError("display_team_id is required")

        if not row.get("team_name"):
            raise ValueError("team_name is required")

    # ✅ Optional UUID fallback
    def get_instance(self, instance_loader, row):
        team_id = row.get("team_id")

        if team_id:
            try:
                return CricketTeam.objects.get(team_id=team_id)
            except CricketTeam.DoesNotExist:
                pass

        return super().get_instance(instance_loader, row)


class CricketMatchDetailsResource(resources.ModelResource):

    # ---------- FOREIGN KEYS ----------

    event = fields.Field(
        column_name="event",
        attribute="event",
        widget=ForeignKeyWidget(CricketEvent, "display_event_id")
    )

    team1 = fields.Field(
        column_name="team1",
        attribute="team1",
        widget=ForeignKeyWidget(CricketTeam, "team_short_name")
    )

    team2 = fields.Field(
        column_name="team2",
        attribute="team2",
        widget=ForeignKeyWidget(CricketTeam, "team_short_name")
    )

    class Meta:
        model = CricketMatchDetails

        # ✅ INCLUDE UUID
        fields = (
            "match_id",
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

        import_id_fields = ("match_id",)

        export_order = fields

        skip_unchanged = True
        report_skipped = True

    # ✅ CRITICAL: protect UUID
    def before_import_row(self, row, **kwargs):
        # 🚫 Never allow UUID overwrite
        row.pop("match_id", None)

        if not row.get("display_match_id"):
            raise ValueError("display_match_id is required")

    # ✅ OPTIONAL: allow UUID fallback (advanced use)
    def get_instance(self, instance_loader, row):
        match_id = row.get("match_id")

        if match_id:
            try:
                return CricketMatchDetails.objects.get(match_id=match_id)
            except CricketMatchDetails.DoesNotExist:
                pass

        return super().get_instance(instance_loader, row)


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
        widget=ForeignKeyWidget(CricketMatchDetails, "display_match_id")
    )

    winner_team = fields.Field(
        column_name="winner_team",
        attribute="winner_team",
        widget=ForeignKeyWidget(CricketTeam, "team_short_name")
    )

    player_of_match = fields.Field(
        column_name="player_of_match",
        attribute="player_of_match",
        widget=ForeignKeyWidget(CricketPlayer, "player_name")
    )

    most_runs_player = fields.Field(
        column_name="most_runs_player",
        attribute="most_runs_player",
        widget=ForeignKeyWidget(CricketPlayer, "player_name")
    )

    most_wickets_taker = fields.Field(
        column_name="most_wickets_taker",
        attribute="most_wickets_taker",
        widget=ForeignKeyWidget(CricketPlayer, "player_name")
    )

    class Meta:
        model = CricketMatchWinnerDetails

        # ✅ INCLUDE UUID
        fields = (
            "winner_id",
            "event",
            "match",
            "winner_team",
            "player_of_match",
            "most_runs_player",
            "most_wickets_taker",
            "created_at",
            "updated_at",
        )

        # ✅ Use match as unique mapping
        import_id_fields = ("match",)

        export_order = fields

        skip_unchanged = True
        report_skipped = True

    # ✅ Protect UUID from overwrite
    def before_import_row(self, row, **kwargs):
        row.pop("winner_id", None)

        if not row.get("match"):
            raise ValueError("match is required")

    # ✅ Optional UUID fallback (advanced)
    def get_instance(self, instance_loader, row):
        winner_id = row.get("winner_id")

        if winner_id:
            try:
                return CricketMatchWinnerDetails.objects.get(winner_id=winner_id)
            except CricketMatchWinnerDetails.DoesNotExist:
                pass

        return super().get_instance(instance_loader, row)
