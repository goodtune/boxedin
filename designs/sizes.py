import json

import cattrs
from attrs import define
from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.migrations.serializer import BaseSerializer


@define(frozen=True)
class DesignSize(object):
    width: int
    height: int


class DesignSizeSerializer(BaseSerializer):
    def serialize(self):
        return (
            json.dumps(cattrs.Converter().unstructure(self.value)),
            {"from designs.sizes import DesignSize"},
        )


class DimensionsJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, DesignSize):
            return cattrs.Converter().unstructure(obj)
        return super().default(obj)


class DimensionsFormField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        # Remove choices from kwargs so parent doesn't process them
        kwargs.pop("encoder", None)
        kwargs.pop("decoder", None)
        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        if isinstance(value, DesignSize):
            return cattrs.unstructure(value)
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                pass
        return super().prepare_value(value)

    def to_python(self, value):
        if isinstance(value, dict):
            return DesignSize(**value)
        if isinstance(value, str):
            try:
                data = json.loads(value)
                if isinstance(data, dict):
                    return DesignSize(**data)
            except Exception:
                pass
        return super().to_python(value)

    def valid_value(self, value):
        if isinstance(value, DesignSize):
            raw = json.dumps(cattrs.unstructure(value))
            for k, v in self.choices:
                if value == k or raw == str(k) or str(value) == str(k):
                    return True
            return False
        return super().valid_value(value)


class DimensionsField(models.JSONField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("encoder", DimensionsJSONEncoder)
        self._raw_choices = kwargs.get("choices")
        if self._raw_choices:
            # Remove choices from kwargs so parent doesn't process them
            kwargs.pop("choices")
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        if isinstance(value, DesignSize):
            return value
        if isinstance(value, dict):
            return DesignSize(**value)
        if isinstance(value, str):
            try:
                data = json.loads(value)
                if isinstance(data, dict):
                    return DesignSize(**data)
            except Exception:
                pass
        return value

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, DesignSize):
            return value
        if isinstance(value, dict):
            return DesignSize(**value)
        if isinstance(value, str):
            try:
                data = json.loads(value)
                if isinstance(data, dict):
                    return DesignSize(**data)
            except Exception:
                pass
        return value

    @property
    def widget_choices(self):
        if not self._raw_choices:
            return []
        return [
            (json.dumps(cattrs.unstructure(choice)), label)
            for choice, label in self._raw_choices
        ]

    def formfield(self, **kwargs):
        defaults = {
            "form_class": DimensionsFormField,
            "choices": self.widget_choices,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
