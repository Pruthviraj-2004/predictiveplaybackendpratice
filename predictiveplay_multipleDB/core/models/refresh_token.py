from django.db import models
import uuid

class RefreshTokenNew(models.Model):
    refresh_token_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    jti = models.CharField(max_length=255, unique=True)
    user_id = models.UUIDField()
    company_display_id = models.CharField(max_length=50)
    is_revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "core_refreshtoken_table"

    def revoke(self):
        self.is_revoked = True
        self.save(update_fields=["is_revoked"])
