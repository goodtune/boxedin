from django.urls import path

from designs import views

urlpatterns = [
    path("collections/", views.CollectionListView.as_view(), name="collection-list"),
    path(
        "collections/<uuid:pk>/",
        views.CollectionDetailView.as_view(),
        name="collection-detail",
    ),
    path(
        "collections/<uuid:collection_pk>/designs/<uuid:pk>/",
        views.DesignDetailView.as_view(),
        name="design-detail",
    ),
]
