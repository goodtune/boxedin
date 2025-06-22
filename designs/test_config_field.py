import json

from django.forms import modelform_factory
from django.test import TestCase

from designs.factories import CollectionFactory, DesignFactory
from designs.fields import ConfigField, ConfigFormField, ConfigFormSet
from designs.models import Design


class ConfigFieldTests(TestCase):
    def test_formfield_class(self):
        field = ConfigField()
        self.assertIsInstance(field.formfield(), ConfigFormField)

    def test_form_validates_formset(self):
        collection = CollectionFactory()
        Form = modelform_factory(Design, fields=["name", "collection", "dimensions"])
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
        # config is not a model field, so we can't check form.cleaned_data["config"]
        # Instead, test ConfigFormField directly

        config_formset = ConfigFormSet(data, prefix="config")
        self.assertTrue(config_formset.is_valid(), config_formset.errors)
        config_field = ConfigFormField()
        config = config_field.clean(config_formset)
        self.assertEqual(
            config,
            {"title": {"class": "django.forms.CharField", "kwargs": {}}},
        )

    def test_edit_existing_config_add_fields(self):
        design = DesignFactory()
        Form = modelform_factory(
            Design,
            fields=["name", "collection", "dimensions"],
        )
        dims = {
            "width": design.dimensions.width,
            "height": design.dimensions.height,
        }
        data = {
            "name": design.name,
            "collection": design.collection.pk,
            "dimensions": json.dumps(dims),
            "config-TOTAL_FORMS": "3",
            "config-INITIAL_FORMS": "1",
            "config-MIN_NUM_FORMS": "0",
            "config-MAX_NUM_FORMS": "1000",
            "config-0-name": "title",
            "config-0-class_name": "django.forms.CharField",
            "config-0-kwargs": '{"max_length": 100}',
            "config-1-name": "home_score",
            "config-1-class_name": "django.forms.IntegerField",
            "config-1-kwargs": "",
            "config-2-name": "away_score",
            "config-2-class_name": "django.forms.IntegerField",
            "config-2-kwargs": "",
        }
        form = Form(data=data, instance=design)
        self.assertTrue(form.is_valid(), form.errors)
        # config is not a model field, so we can't check form.cleaned_data["config"]
        from designs.fields import ConfigFormField, ConfigFormSet

        config_formset = ConfigFormSet(data, prefix="config")
        self.assertTrue(config_formset.is_valid(), config_formset.errors)
        config_field = ConfigFormField()
        config = config_field.clean(config_formset)
        self.assertEqual(
            set(config.keys()),
            {"title", "home_score", "away_score"},
        )
        self.assertEqual(
            config["home_score"],
            {"class": "django.forms.IntegerField", "kwargs": {}},
        )
        self.assertEqual(
            config["away_score"],
            {"class": "django.forms.IntegerField", "kwargs": {}},
        )
