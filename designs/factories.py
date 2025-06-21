import factory

from designs.models import Collection, Design, DesignRender
from designs.sizes import DesignSize


class CollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collection

    name = factory.Sequence(lambda n: f"Collection {n}")
    description = factory.Faker("paragraph")


class DesignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Design

    name = factory.Sequence(lambda n: f"Design {n}")
    description = factory.Faker("paragraph")
    dimensions = factory.Iterator(
        [DesignSize(1080, 1920), DesignSize(1920, 1080), DesignSize(1080, 1080)]
    )

    template = "<svg>{{ title }}</svg>"
    config = {
        "title": {
            "class": "django.forms.CharField",
            "kwargs": {"max_length": 100},
        }
    }

    collection = factory.SubFactory(CollectionFactory)


class DesignRenderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DesignRender

    design = factory.SubFactory(DesignFactory)
    template = factory.SelfAttribute("design.template")
    config = factory.SelfAttribute("design.config")
    values = {"title": "Test"}
