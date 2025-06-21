from django.views.generic import DetailView, ListView

from designs.models import Collection, Design


class CollectionListView(ListView):
    model = Collection
    template_name = "designs/collection_list.html"
    context_object_name = "collections"


class CollectionDetailView(DetailView):
    model = Collection
    template_name = "designs/collection_detail.html"
    context_object_name = "collection"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["designs"] = self.object.designs.all()
        return context


class DesignDetailView(DetailView):
    model = Design
    template_name = "designs/design_detail.html"
    context_object_name = "design"

    def get_queryset(self):
        qs = super().get_queryset()
        collection_pk = self.kwargs.get("collection_pk")
        if collection_pk:
            qs = qs.filter(collection__pk=collection_pk)
        return qs
