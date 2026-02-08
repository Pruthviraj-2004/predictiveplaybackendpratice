from django.db import models
from django.utils import timezone


class RefreshToken(models.Model):
    jti = models.CharField(max_length=255, unique=True)
    user_id = models.BigIntegerField()
    company_display_id = models.CharField(max_length=50)

    is_revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    expires_at = models.DateTimeField()

    def revoke(self):
        self.is_revoked = True
        self.save(update_fields=["is_revoked"])
