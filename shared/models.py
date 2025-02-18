from django.db import models
from uuid import uuid4


class BaseModel(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, null=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # It means this model is aimed for inheritance and will not be saved in database.