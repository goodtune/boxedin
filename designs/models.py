import json
import uuid

from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django import forms
from django.db import models
from django.db.migrations.writer import MigrationWriter
from django.template import Context, Template
from django.utils.module_loading import import_string
from markdownfield.models import MarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

from designs.sizes import DesignSize, DesignSizeSerializer, DimensionsField
from designs.fields import ConfigField

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
    template = models.TextField(default="")
    config = ConfigField(default=dict)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        context = {k: "" for k in (self.config or {}).keys()}
        try:
            Template(self.template).render(Context(context))
        except Exception as exc:  # pragma: no cover - error branch
            raise ValidationError({"template": str(exc)})

    def get_config_form_class(self):
        fields = {}
        for key, data in (self.config or {}).items():
            cls = import_string(data.get("class"))
            kwargs = data.get("kwargs", {})
            fields[key] = cls(**kwargs)
        return type("DesignConfigForm", (forms.Form,), fields)


class DesignRender(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design = models.ForeignKey(
        Design, related_name="renders", on_delete=models.CASCADE
    )
    template = models.TextField(default="")
    config = ConfigField(default=dict)
    values = models.JSONField(default=dict, encoder=DjangoJSONEncoder)

    def __str__(self):
        return f"Render of {self.design.name}"
