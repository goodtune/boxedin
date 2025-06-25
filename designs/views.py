from django.views.generic import DetailView, ListView
from django.views.generic.base import View
import fontconfig
from django.shortcuts import render

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


class FontListView(View):
    template_name = "designs/font_list.html"

    def get(self, request, *args, **kwargs):
        filters = {}
        group_by = request.GET.get("group_by")

        # Apply filters based on query parameters
        for param in ["lang", "family", "style"]:
            value = request.GET.get(param)
            if value:
                filters[param] = value

        # Query fonts using fontconfig with filters
        fonts = [fontconfig.FcFont(f) for f in fontconfig.query(**filters)]

        # Group fonts if group_by is specified
        if group_by:
            grouped_fonts = {}
            for font in fonts:
                key = getattr(font, group_by, {}).get("en", "Unknown")
                grouped_fonts.setdefault(key, []).append(font)
            context = {"grouped_fonts": grouped_fonts}
        else:
            context = {"fonts": fonts}

        return render(request, self.template_name, context)
