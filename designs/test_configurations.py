from django.forms import inlineformset_factory
from django.test import TestCase

from designs.factories import CollectionFactory, DesignFactory
from designs.models import Design, DesignConfiguration


class DesignConfigurationFormsetTests(TestCase):
    def test_create_config_via_formset(self):
        collection = CollectionFactory()
        design = DesignFactory(collection=collection, config={})
        FormSet = inlineformset_factory(
            Design,
            DesignConfiguration,
            fields=["name", "field_class", "field_kwargs"],
            extra=1,
            can_delete=True,
        )
        data = {
            "config-TOTAL_FORMS": "1",
            "config-INITIAL_FORMS": "0",
            "config-MIN_NUM_FORMS": "0",
            "config-MAX_NUM_FORMS": "1000",
            "config-0-name": "title",
            "config-0-field_class": "django.forms.CharField",
            "config-0-field_kwargs": "{}",
        }
        formset = FormSet(data=data, instance=design, prefix="config")
        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()
        design.refresh_from_db()
        self.assertEqual(design.config, {
            "title": {"class": "django.forms.CharField", "kwargs": {}}
        })

    def test_edit_existing_config_add_fields(self):
        design = DesignFactory()
        FormSet = inlineformset_factory(
            Design,
            DesignConfiguration,
            fields=["name", "field_class", "field_kwargs"],
            extra=1,
            can_delete=True,
        )
        first = design.configurations.first()
        data = {
            "config-TOTAL_FORMS": "3",
            "config-INITIAL_FORMS": "1",
            "config-MIN_NUM_FORMS": "0",
            "config-MAX_NUM_FORMS": "1000",
            "config-0-id": str(first.pk),
            "config-0-name": first.name,
            "config-0-field_class": first.field_class,
            "config-0-field_kwargs": "{\"max_length\": 100}",
            "config-1-name": "home_score",
            "config-1-field_class": "django.forms.IntegerField",
            "config-1-field_kwargs": "{}",
            "config-2-name": "away_score",
            "config-2-field_class": "django.forms.IntegerField",
            "config-2-field_kwargs": "{}",
        }
        formset = FormSet(data=data, instance=design, prefix="config")
        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()
        design.refresh_from_db()
        self.assertEqual(
            set(design.config.keys()), {"title", "home_score", "away_score"}
        )
        self.assertEqual(
            design.config["home_score"],
            {"class": "django.forms.IntegerField", "kwargs": {}},
        )
        self.assertEqual(
            design.config["away_score"],
            {"class": "django.forms.IntegerField", "kwargs": {}},
        )
