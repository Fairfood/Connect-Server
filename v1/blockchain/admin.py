from django.contrib import admin

from .models.callback_auth import CallBackToken

from .models.request import BlockchainRequest
from .models.request import CallbackResponse
from .library import format_json_readonly

# Register your models here.

from django.contrib import admin


def retry_request(modeladmin, request, queryset):
    for item in queryset:
        item.retry()


retry_request.short_description = "Retry request"


class ResponseInline(admin.TabularInline):

    def response(self, obj):
        """Function to format response json."""
        short_description = 'response'
        return format_json_readonly(obj.data)

    model = CallbackResponse
    readonly_fields = ['created_on', 'response', 'success']
    fields = ['response', 'created_on', 'success']
    extra = 0


class CallBackTokenAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_on', 'updated_on')
    list_display = ('id', 'key', 'status')


class RequestAdmin(admin.ModelAdmin):

    def request_response(self, obj):
        """Function to format response json."""
        short_description = 'request_response'
        return format_json_readonly(obj.response)

    def request_body(self, obj):
        """Function to format response json."""
        short_description = 'request_response'
        return format_json_readonly(obj.body)

    readonly_fields = (
        'status', 'created_on', 'request_body', 'request_response',
        'id', 'updated_on', 'creator', 'receipt', 'callback_token',
        'object_related_name', 'password', 'last_api_call'
    )
    exclude = ('type', 'response', 'body')
    list_display = (
        '__str__', 'id', 'status', 'created_on', 'last_api_call'
    )
    inlines = [
        ResponseInline,
    ]
    list_filter = (
        'type', 'status', 'created_on')

    actions = [retry_request]


admin.site.register(CallBackToken, CallBackTokenAdmin)
admin.site.register(CallbackResponse)
admin.site.register(BlockchainRequest, RequestAdmin)
for subclass in BlockchainRequest.__subclasses__():
    admin.site.register(subclass, RequestAdmin)
