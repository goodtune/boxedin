from django.test import TestCase
from django.core.exceptions import ValidationError

from django import forms

from designs.factories import CollectionFactory, DesignFactory, DesignRenderFactory
from designs.models import Collection, Design, DesignRender
from designs.sizes import DesignSize


class ModelTests(TestCase):

    def test_collection(self):
        collection = CollectionFactory()
        self.assertQuerySetEqual(Collection.objects.all(), [collection])
        self.assertEqual(str(collection), collection.name)

    def test_design(self):
        design = DesignFactory()
        self.assertQuerySetEqual(Design.objects.all(), [design])
        self.assertEqual(str(design), design.name)

    def test_design_dimensions_type(self):
        DesignFactory(name="Test Design", dimensions=DesignSize(1080, 1920))
        self.assertEqual(
            [o.dimensions for o in Design.objects.all()],
            [DesignSize(1080, 1920)],
        )

    def test_design_dimensions_fields(self):
        DesignFactory(name="Test Design", dimensions=DesignSize(1080, 1920))
        self.assertQuerySetEqual(
            Design.objects.values("name", "dimensions__width", "dimensions__height"),
            [
                {
                    "name": "Test Design",
                    "dimensions__width": 1080,
                    "dimensions__height": 1920,
                }
            ],
        )

    def test_design_template_clean(self):
        design = DesignFactory(template="{% if %}")
        with self.assertRaises(ValidationError):
            design.full_clean()

    def test_get_config_form_class(self):
        design = DesignFactory()
        FormClass = design.get_config_form_class()
        form = FormClass()
        self.assertIn("title", form.fields)
        self.assertIsInstance(form.fields["title"], forms.CharField)

    def test_design_render(self):
        render = DesignRenderFactory()
        self.assertIsInstance(render, DesignRender)
        self.assertEqual(render.template, render.design.template)
