from django.forms import modelform_factory
from django.test import TestCase

from designs.factories import CollectionFactory
from designs.models import Design


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
