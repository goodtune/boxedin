import json

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import formset_factory, BaseFormSet
from django.db import models


class ConfigItemForm(forms.Form):
    name = forms.CharField()
    class_name = forms.ChoiceField(
        choices=[
            ("django.forms.CharField", "CharField"),
            ("django.forms.IntegerField", "IntegerField"),
        ]
    )
    kwargs = forms.CharField(required=False)

    def clean_kwargs(self):
        data = self.cleaned_data.get("kwargs")
        if not data:
            return {}
        try:
            value = json.loads(data)
            if not isinstance(value, dict):
                raise ValueError()
            return value
        except Exception as exc:  # pragma: no cover - error branch
            raise forms.ValidationError("Enter a valid JSON object") from exc


ConfigFormSet = formset_factory(ConfigItemForm, extra=1, can_delete=True)


class ConfigWidget(forms.Widget):
    template_name = "designs/widgets/config_widget.html"

    def __init__(self, formset_class=None, attrs=None):
        self.formset_class = formset_class or ConfigFormSet
        super().__init__(attrs)

    def format_initial(self, value):
        if not value:
            return []
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except Exception:
                value = {}
        if not isinstance(value, dict):
            return []
        initial = []
        for name, conf in value.items():
            initial.append(
                {
                    "name": name,
                    "class_name": conf.get("class", ""),
                    "kwargs": json.dumps(conf.get("kwargs", {})),
                }
            )
        return initial

    def get_formset(self, name, data=None, value=None):
        if data is not None:
            return self.formset_class(data, prefix=name)
        initial = self.format_initial(value)
        return self.formset_class(prefix=name, initial=initial)

    def value_from_datadict(self, data, files, name):
        formset = self.get_formset(name, data=data)
        return formset

    def get_context(self, name, value, attrs):
        formset = self.get_formset(name, value=value)
        context = super().get_context(name, value, attrs)
        context["formset"] = formset
        context["name"] = name
        return context


class ConfigFormField(forms.Field):
    widget = ConfigWidget

    def __init__(self, *args, formset_class=None, **kwargs):
        self.formset_class = formset_class or ConfigFormSet
        kwargs.pop("encoder", None)
        kwargs.pop("decoder", None)
        kwargs.setdefault("required", False)
        kwargs["widget"] = self.widget(formset_class=self.formset_class)
        super().__init__(*args, **kwargs)

    def clean(self, value):
        formset = value
        if not isinstance(formset, BaseFormSet):
            formset = self.formset_class()
        if not formset.is_valid():
            raise forms.ValidationError(formset.errors)
        config = {}
        for cleaned in formset.cleaned_data:
            if cleaned and not cleaned.get("DELETE"):
                config[cleaned["name"]] = {
                    "class": cleaned["class_name"],
                    "kwargs": cleaned.get("kwargs", {}),
                }
        return config


class ConfigField(models.JSONField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("encoder", DjangoJSONEncoder)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"form_class": ConfigFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
