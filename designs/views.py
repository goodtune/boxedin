from django.views.generic import DetailView, ListView
from django.views.generic.base import View
import fontconfig
from django.shortcuts import render

from designs.forms import FontFilterForm

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
        form = FontFilterForm(request.GET)
        fonts = []
        grouped_fonts = None
        if form.is_valid():
            filters = form.get_filters()
            fonts = [fontconfig.FcFont(f) for f in fontconfig.query(**filters)]
            group_by = form.cleaned_data.get("group_by")
            if group_by:
                grouped_fonts = {}
                for font in fonts:
                    attr = getattr(font, group_by, {})
                    if isinstance(attr, dict):
                        key = attr.get("en") or next(iter(attr.values()), "Unknown")
                    else:
                        key = attr or "Unknown"
                    grouped_fonts.setdefault(key, []).append(font)
                grouped_fonts = dict(sorted(grouped_fonts.items()))

        context = {
            "form": form,
            "fonts": fonts if grouped_fonts is None else None,
            "grouped_fonts": grouped_fonts,
        }

        return render(request, self.template_name, context)
