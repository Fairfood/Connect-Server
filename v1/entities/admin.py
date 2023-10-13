"""Models are registered with django admin at here."""

from django.contrib import admin

from base.db.admin import BaseAdmin

from v1.entities import models as entity_models


class EntityAdmin(BaseAdmin):
    list_display = ('name', 'id', 'type')
    list_filter = ('type',)
    search_fields = ['name']


class EntityDocumentAdmin(BaseAdmin):
    list_display = ('name', 'id', )
    search_fields = ['name']


class EntityMemberAdmin(BaseAdmin):
    list_display = ('user', 'entity', 'id',)
    list_filter = ('is_active', 'type',)
    search_fields = ['user__name']


admin.site.register(entity_models.Entity, EntityAdmin)
admin.site.register(entity_models.EntityDocument, EntityDocumentAdmin)
admin.site.register(entity_models.EntityMember, EntityMemberAdmin)
