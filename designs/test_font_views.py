from types import SimpleNamespace
from unittest.mock import patch

from test_plus.test import TestCase


class FontListViewTests(TestCase):
    url_name = "font-list"

    def setUp(self):
        self.font1 = SimpleNamespace(family={"en": "A"}, style={"en": "Regular"}, lang="en")
        self.font2 = SimpleNamespace(family={"en": "B"}, style={"en": "Bold"}, lang="en")

    @patch("designs.views.fontconfig.FcFont")
    @patch("designs.views.fontconfig.query")
    def test_filters_and_grouping(self, mock_query, mock_fcfont):
        mock_query.return_value = ["f1", "f2"]
        mock_fcfont.side_effect = [self.font1, self.font2]
        response = self.get(self.url_name, data={"lang": "en", "group_by": "family"})
        self.response_200(response)
        mock_query.assert_called_with(lang="en")
        self.assertIn("grouped_fonts", response.context)
        self.assertIn("A", response.context["grouped_fonts"]) 
        self.assertTrue(response.context["form"].is_valid())

    @patch("designs.views.fontconfig.FcFont")
    @patch("designs.views.fontconfig.query")
    def test_no_grouping(self, mock_query, mock_fcfont):
        mock_query.return_value = ["f1"]
        mock_fcfont.return_value = self.font1
        response = self.get(self.url_name, data={"family": "A"})
        self.response_200(response)
        mock_query.assert_called_with(family="A")
        self.assertIn("fonts", response.context)
        self.assertTrue(response.context["form"].is_valid())

