from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from core.models.cricket_event import CricketEvent
from core.resources import CricketEventResource


@admin.register(CricketEvent)
class CricketEventAdmin(ImportExportModelAdmin):
    resource_class = CricketEventResource

    list_display = (
        "display_event_id",
        "event_name",
        "start_date",
        "end_date",
        "is_public",
        "allow_predictions",
        "is_featured",
    )

    list_filter = (
        "is_public",
        "allow_predictions",
        "is_featured",
    )

    search_fields = (
        "event_name",
        "short_name",
        "display_event_id",
    )

    ordering = ("-start_date",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Event Info", {
            "fields": (
                "display_event_id",
                "event_name",
                "short_name",
                "logo_url",
                "organizer",
                "location",
                "status",
            )
        }),
        ("Schedule", {
            "fields": (
                "start_date",
                "end_date",
            )
        }),
        ("Visibility & Rules", {
            "fields": (
                "is_public",
                "allow_predictions",
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