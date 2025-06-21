from django.contrib import admin

from designs.models import Collection, Design, DesignRender


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)
    ordering = ("name",)


@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = ("name", "dimensions")
    search_fields = ("name",)
    list_filter = ("dimensions",)


@admin.register(DesignRender)
class DesignRenderAdmin(admin.ModelAdmin):
    list_display = ("id", "design")
