from django.contrib import admin

# Register your models here.


class ClientAccessTokenAdmin(admin.ModelAdmin):
    list_display = ("token", "user", "company", "application", "expires")
    list_select_related = ("application", "user")
    raw_id_fields = ("user", "source_refresh_token")
    search_fields = ("token",)
    list_filter = ("application",)
