from django.forms import modelform_factory
from django.test import TestCase

from designs.factories import CollectionFactory
from designs.models import Design
from designs.sizes import DesignSize


class DesignFormFieldTests(TestCase):
    def test_invalid_dimensions_json(self):
        collection = CollectionFactory()
        Form = modelform_factory(Design, fields=["name", "collection", "dimensions"])
        form = Form(
            data={
                "name": "Test Design",
                "collection": collection.pk,
                "dimensions": '{"width":999,"height":999}',
            }
        )
        self.assertFormError(
            form,
            "dimensions",
            "Select a valid choice. DesignSize(width=999, height=999) is not one of the available choices.",
        )

    def test_create_design_from_form(self):
        collection = CollectionFactory()
        Form = modelform_factory(Design, fields=["name", "collection", "dimensions"])
        form = Form(
            data={
                "name": "Valid Design",
                "collection": collection.pk,
                "dimensions": '{"width": 1080, "height": 1920}',
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        design = form.save()
        self.assertEqual(design.collection, collection)
        self.assertEqual(design.dimensions, DesignSize(1080, 1920))

    def test_config_field_formset(self):
        collection = CollectionFactory()
        Form = modelform_factory(
            Design,
            fields=["name", "collection", "dimensions", "config"],
        )
        data = {
            "name": "Config Design",
            "collection": collection.pk,
            "dimensions": '{"width": 1080, "height": 1920}',
            "config-TOTAL_FORMS": "1",
            "config-INITIAL_FORMS": "0",
            "config-MIN_NUM_FORMS": "0",
            "config-MAX_NUM_FORMS": "1000",
            "config-0-name": "title",
            "config-0-class_name": "django.forms.CharField",
            "config-0-kwargs": "{\"max_length\": 50}",
        }
        form = Form(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        design = form.save(commit=False)
        self.assertIn("title", design.config)
        self.assertEqual(
            design.config["title"],
            {"class": "django.forms.CharField", "kwargs": {"max_length": 50}},
        )
