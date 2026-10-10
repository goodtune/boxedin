from types import SimpleNamespace
from unittest.mock import patch

from test_plus.test import TestCase


def make_font(family, style, languages):
    """Stand-in for fontconfig.FcFont, which exposes languages via a method."""
    return SimpleNamespace(
        family={"en": family},
        style={"en": style},
        get_languages=lambda: list(languages),
    )


class FontListViewTests(TestCase):
    url_name = "font-list"

    def setUp(self):
        self.fonts = {
            "a.ttf": make_font("A", "Regular", ["en", "fr"]),
            "b.ttf": make_font("B", "Bold", ["en"]),
        }
        patcher = patch("designs.views.fontconfig")
        self.fontconfig = patcher.start()
        self.addCleanup(patcher.stop)
        self.fontconfig.query.side_effect = self.query
        self.fontconfig.FcFont.side_effect = self.fonts.__getitem__

    def query(self, *, family=None, lang=None):
        """Stand-in for fontconfig.query, which only accepts family and lang."""
        return [
            path
            for path, font in self.fonts.items()
            if family in (None, font.family["en"]) and lang in (None, *font.get_languages())
        ]

    def test_filters_and_grouping(self):
        response = self.get(self.url_name, data={"lang": "en", "group_by": "family"})
        self.response_200(response)
        self.fontconfig.query.assert_called_with(lang="en")
        self.assertEqual(list(response.context["grouped_fonts"]), ["A", "B"])
        self.assertTrue(response.context["form"].is_valid())

    def test_no_grouping(self):
        response = self.get(self.url_name, data={"family": "A"})
        self.response_200(response)
        self.fontconfig.query.assert_called_with(family="A")
        self.assertIsNone(response.context["grouped_fonts"])
        self.assertTrue(response.context["form"].is_valid())

    def test_style_filter(self):
        response = self.get(self.url_name, data={"style": "bold"})
        self.response_200(response)
        self.fontconfig.query.assert_called_with()
        self.assertEqual(response.context["fonts"], [self.fonts["b.ttf"]])

    def test_group_by_language(self):
        response = self.get(self.url_name, data={"group_by": "lang"})
        self.response_200(response)
        grouped = response.context["grouped_fonts"]
        self.assertEqual(list(grouped), ["en", "fr"])
        self.assertEqual(grouped["en"], [self.fonts["a.ttf"], self.fonts["b.ttf"]])
        self.assertEqual(grouped["fr"], [self.fonts["a.ttf"]])

    def test_group_by_language_with_lang_filter(self):
        response = self.get(self.url_name, data={"lang": "fr", "group_by": "lang"})
        self.response_200(response)
        self.assertEqual(list(response.context["grouped_fonts"]), ["fr"])
