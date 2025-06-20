from django.test import TestCase

from designs.factories import CollectionFactory, DesignFactory
from designs.models import Collection, Design
from designs.sizes import DesignSize


class ModelTests(TestCase):

    def test_collection(self):
        collection = CollectionFactory()
        self.assertQuerySetEqual(Collection.objects.all(), [collection])

    def test_design(self):
        design = DesignFactory()
        self.assertQuerySetEqual(Design.objects.all(), [design])

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
