from django import forms
from django.test import TestCase

from designs.sizes import (
    DesignSize,
    DesignSizeSerializer,
    DimensionsField,
    DimensionsFormField,
    DimensionsJSONEncoder,
)


class SizesExtraTests(TestCase):
    def test_design_size_serializer(self):
        test_cases = [
            (
                DesignSize(100, 200),
                (
                    '{"width": 100, "height": 200}',
                    {"from designs.sizes import DesignSize"},
                ),
            ),
        ]
        for ds, (expected_data, expected_imports) in test_cases:
            with self.subTest(input=ds):
                ser = DesignSizeSerializer(ds)
                data, imports = ser.serialize()
                self.assertEqual(expected_data, data)
                self.assertEqual(expected_imports, imports)

    def test_dimensions_json_encoder(self):
        enc = DimensionsJSONEncoder()
        test_cases = [
            (DesignSize(10, 20), '{"width": 10, "height": 20}'),
            ({"foo": "bar"}, '{"foo": "bar"}'),
        ]
        for value, expected in test_cases:
            with self.subTest(input=value):
                result = enc.encode(value)
                self.assertEqual(expected, result)

    def test_dimensions_json_encoder_fallback(self):
        enc = DimensionsJSONEncoder()

        class Unserializable:
            pass

        with self.assertRaises(TypeError):
            enc.encode(Unserializable())

    def test_dimensions_form_field_prepare_value(self):
        field = DimensionsFormField(choices=[("a", "A")])
        test_cases = [
            (DesignSize(1, 2), {"width": 1, "height": 2}),
            ('{"width":3,"height":4}', {"width": 3, "height": 4}),
            ("a", "a"),
        ]
        for value, expected in test_cases:
            with self.subTest(input=value):
                self.assertEqual(field.prepare_value(value), expected)
        # str branch (invalid JSON)
        self.assertIsNotNone(field.prepare_value("notjson"))

    def test_dimensions_form_field_prepare_value_invalid_json(self):
        field = DimensionsFormField(choices=[("a", "A")])
        self.assertIsNotNone(field.prepare_value("notjson"))

    def test_dimensions_form_field_to_python(self):
        field = DimensionsFormField(choices=[("a", "A")])
        test_cases = [
            ({"width": 5, "height": 6}, DesignSize(5, 6)),
            ('{"width":7,"height":8}', DesignSize(7, 8)),
            ("a", "a"),
        ]
        for value, expected in test_cases:
            with self.subTest(input=value):
                self.assertEqual(field.to_python(value), expected)
        # str branch (invalid JSON)
        self.assertIsNotNone(field.to_python("notjson"))

    def test_dimensions_form_field_to_python_invalid_json(self):
        field = DimensionsFormField(choices=[("a", "A")])
        self.assertIsNotNone(field.to_python("notjson"))

    def test_dimensions_field_from_db_value(self):
        field = DimensionsField()
        test_cases = [
            (None, None),
            (DesignSize(9, 10), DesignSize(9, 10)),
            ({"width": 11, "height": 12}, DesignSize(11, 12)),
            ('{"width":13,"height":14}', DesignSize(13, 14)),
            ("notjson", "notjson"),
        ]
        for value, expected in test_cases:
            with self.subTest(input=value):
                self.assertEqual(field.from_db_value(value, None, None), expected)

    def test_dimensions_field_to_python(self):
        field = DimensionsField()
        test_cases = [
            (None, None),
            (DesignSize(15, 16), DesignSize(15, 16)),
            ({"width": 17, "height": 18}, DesignSize(17, 18)),
            ('{"width":19,"height":20}', DesignSize(19, 20)),
            ("notjson", "notjson"),
        ]
        for value, expected in test_cases:
            with self.subTest(input=value):
                self.assertEqual(field.to_python(value), expected)

    def test_dimensions_field_widget_choices(self):
        # No choices
        field = DimensionsField()
        self.assertEqual(field.widget_choices, [])
        # With choices
        choices = [
            (DesignSize(21, 22), "Label1"),
            (DesignSize(23, 24), "Label2"),
        ]
        field2 = DimensionsField(choices=choices)
        widget_choices = field2.widget_choices
        self.assertEqual(len(widget_choices), 2)
        self.assertIn("Label1", [lbl for _, lbl in widget_choices])

    def test_dimensions_field_formfield(self):
        field = DimensionsField()
        form_field = field.formfield()
        self.assertIsInstance(form_field, DimensionsFormField)
        # With extra kwargs
        form_field2 = field.formfield(widget=forms.TextInput)
        self.assertIsInstance(form_field2, DimensionsFormField)
