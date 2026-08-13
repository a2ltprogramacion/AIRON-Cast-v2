"""
URLs para la app reply.
"""
from django.urls import path
from reply import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("upload/", views.upload_excel, name="upload_excel"),
    path("search/", views.search_templates, name="search_templates"),
    path("import/individual/", views.import_individual, name="import_individual"),
    path("import/bulk/", views.import_bulk, name="import_bulk"),
    path("api/templates/", views.api_templates_list, name="api_templates_list"),
    path("delete/<int:template_id>/", views.delete_template, name="delete_template"),
    path("edit/<int:template_id>/", views.edit_template, name="edit_template"),
]