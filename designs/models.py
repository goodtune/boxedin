import uuid

from django.db import models
from django.db.migrations.writer import MigrationWriter
from markdownfield.models import MarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

from designs.sizes import DesignSize, DesignSizeSerializer, DimensionsField

DIMENSIONS = (
    (DesignSize(1080, 1920), "Story"),
    (DesignSize(1920, 1080), "Landscape"),
    (DesignSize(1080, 1080), "Square"),
)


MigrationWriter.register_serializer(DesignSize, DesignSizeSerializer)


class Collection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = MarkdownField(
        validator=VALIDATOR_STANDARD,
        use_editor=True,
        use_admin_editor=True,
    )

    def __str__(self):
        return self.name


class Design(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    collection = models.ForeignKey(
        Collection,
        related_name="designs",
        on_delete=models.CASCADE,
    )

    dimensions = DimensionsField(choices=DIMENSIONS)

    def __str__(self):
        return self.name
