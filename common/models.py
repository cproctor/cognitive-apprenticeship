from django.db import models

class NondeletedManager(models.Manager):
    "A model manager which excludes deleted objects"
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)

