from django.forms import modelform_factory
from django.test import TestCase

from designs.factories import CollectionFactory
from designs.fields import ConfigField, ConfigFormField
from designs.models import Design


class ConfigFieldTests(TestCase):
    def test_formfield_class(self):
        field = ConfigField()
        self.assertIsInstance(field.formfield(), ConfigFormField)

    def test_form_validates_formset(self):
        collection = CollectionFactory()
        Form = modelform_factory(Design, fields=["name", "collection", "dimensions", "config"])
        data = {
            "name": "Cfg",
            "collection": collection.pk,
            "dimensions": '{"width": 1080, "height": 1920}',
            "config-TOTAL_FORMS": "1",
            "config-INITIAL_FORMS": "0",
            "config-MIN_NUM_FORMS": "0",
            "config-MAX_NUM_FORMS": "1000",
            "config-0-name": "title",
            "config-0-class_name": "django.forms.CharField",
            "config-0-kwargs": "",
        }
        form = Form(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data["config"],
            {"title": {"class": "django.forms.CharField", "kwargs": {}}},
        )
