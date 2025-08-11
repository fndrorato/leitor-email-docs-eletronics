from django.db import models


class User(models.Model):
    """
    Model representing a user in the system.
    """
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    host = models.CharField(max_length=128, blank=True)
    port = models.CharField(max_length=128, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.username
