from django.db import models
from django.conf import settings

class FinanceInfo(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title