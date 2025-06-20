import factory

from designs.models import Collection, Design
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

    collection = factory.SubFactory(CollectionFactory)
