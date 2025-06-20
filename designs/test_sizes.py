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
        ds = DesignSize(100, 200)
        ser = DesignSizeSerializer(ds)
        data, imports = ser.serialize()
        self.assertEqual('{"width": 100, "height": 200}', data)
        self.assertEqual({"from designs.sizes import DesignSize"}, imports)

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
        # DesignSize branch
        ds = DesignSize(1, 2)
        self.assertEqual(field.prepare_value(ds), {"width": 1, "height": 2})
        # str branch (valid JSON)
        self.assertEqual(
            field.prepare_value('{"width":3,"height":4}'), {"width": 3, "height": 4}
        )
        # str branch (invalid JSON)
        self.assertIsNotNone(field.prepare_value("notjson"))
        # fallback to super
        self.assertEqual(field.prepare_value("a"), "a")

    def test_dimensions_form_field_to_python(self):
        field = DimensionsFormField(choices=[("a", "A")])
        # dict branch
        self.assertEqual(field.to_python({"width": 5, "height": 6}), DesignSize(5, 6))
        # str branch (valid JSON)
        self.assertEqual(field.to_python('{"width":7,"height":8}'), DesignSize(7, 8))
        # str branch (invalid JSON)
        self.assertIsNotNone(field.to_python("notjson"))
        # fallback to super
        self.assertEqual(field.to_python("a"), "a")

    def test_dimensions_field_from_db_value(self):
        field = DimensionsField()
        # None branch
        self.assertIsNone(field.from_db_value(None, None, None))
        # DesignSize branch
        ds = DesignSize(9, 10)
        self.assertEqual(field.from_db_value(ds, None, None), ds)
        # dict branch
        self.assertEqual(
            field.from_db_value({"width": 11, "height": 12}, None, None),
            DesignSize(11, 12),
        )
        # str branch (valid JSON)
        self.assertEqual(
            field.from_db_value('{"width":13,"height":14}', None, None),
            DesignSize(13, 14),
        )
        # str branch (invalid JSON)
        self.assertEqual(field.from_db_value("notjson", None, None), "notjson")

    def test_dimensions_field_to_python(self):
        field = DimensionsField()
        # None branch
        self.assertIsNone(field.to_python(None))
        # DesignSize branch
        ds = DesignSize(15, 16)
        self.assertEqual(field.to_python(ds), ds)
        # dict branch
        self.assertEqual(
            field.to_python({"width": 17, "height": 18}), DesignSize(17, 18)
        )
        # str branch (valid JSON)
        self.assertEqual(
            field.to_python('{"width":19,"height":20}'), DesignSize(19, 20)
        )
        # str branch (invalid JSON)
        self.assertEqual(field.to_python("notjson"), "notjson")

    def test_dimensions_field_widget_choices(self):
        # No choices
        field = DimensionsField()
        self.assertEqual(field.widget_choices, [])
        # With choices
        choices = [(DesignSize(21, 22), "Label1"), (DesignSize(23, 24), "Label2")]
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
