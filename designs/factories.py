import factory

from designs.models import (
    Collection,
    Design,
    DesignRender,
    DesignConfiguration,
)
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

    template = "<svg>{{ title }}" "</svg>"

    collection = factory.SubFactory(CollectionFactory)

    @factory.post_generation
    def config(self, create, extracted, **kwargs):
        if not create:
            return
        default = {
            "title": {
                "class": "django.forms.CharField",
                "kwargs": {"max_length": 100},
            }
        }
        data = extracted if extracted is not None else default
        for name, conf in data.items():
            DesignConfiguration.objects.create(
                design=self,
                name=name,
                field_class=conf["class"],
                field_kwargs=conf.get("kwargs", {}),
            )


class DesignRenderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DesignRender

    design = factory.SubFactory(DesignFactory)
    template = factory.SelfAttribute("design.template")
    config = factory.SelfAttribute("design.config")
    values = {"title": "Test"}
