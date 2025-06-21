from test_plus.test import TestCase

from designs.factories import CollectionFactory, DesignFactory


class CollectionViewTests(TestCase):
    def setUp(self):
        self.collection = CollectionFactory()
        self.design = DesignFactory(collection=self.collection)

    def test_markdown_rendered_as_html(self):
        self.collection.description = "This **is** bold"
        self.collection.save()

        response = self.get("collection-detail", pk=self.collection.pk)
        self.response_200(response)
        self.assertContains(response, "<strong>is</strong>", html=True)

    def test_collection_list_view(self):
        response = self.get("collection-list")
        self.response_200(response)
        self.assertContains(response, self.collection.name)

    def test_collection_detail_view(self):
        response = self.get("collection-detail", pk=self.collection.pk)
        self.response_200(response)
        self.assertContains(response, self.collection.name)
        self.assertContains(response, self.design.name)

    def test_design_detail_view(self):
        response = self.get(
            "design-detail", collection_pk=self.collection.pk, pk=self.design.pk
        )
        self.response_200(response)
        self.assertContains(response, self.design.name)
        self.assertContains(response, self.collection.name)
