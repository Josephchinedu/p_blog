from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from main.models import Post


# Register your models here.
class PostResource(resources.ModelResource):
    class Meta:
        model = Post


class PostResourceAdmin(ImportExportModelAdmin):
    resource_class = PostResource
    search_fields = [
        "created_by__email",
        "created_by__username",
        "created_by__first_name",
        "created_by__last_name",
    ]
    list_filter = ("created_at",)
    date_hierarchy = "created_at"

    raw_id_fields = ["created_by"]

    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]


admin.site.register(Post, PostResourceAdmin)
