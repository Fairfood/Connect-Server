"""
Serializers for notifications.
"""

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from base.drf import fields

from v1.notifications.models import Notification

from v1.accounts.serializers import user as user_serializers


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer to get summary of count of notifications per entity per user
    """
    id = fields.SerializableRelatedField(read_only=True)
    actor_entity = fields.SerializableRelatedField(read_only=True)
    target_entity = fields.SerializableRelatedField(read_only=True)
    event_id = fields.SerializableRelatedField(read_only=True)
    created_on = fields.UnixDateTimeField(read_only=True)
    event_type = serializers.CharField(source='event_type.name', default=None)
    redirect_id = fields.SerializableRelatedField(read_only=True)
    creator = fields.SerializableRelatedField(
        serializer=user_serializers.BasicUserSerializer, read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id', 'is_read', 'title', 'body', 'actor_entity',
            'target_entity', 'event_id', 'event_type',
            'created_on', 'redirect_id', 'redirect_type', 'creator'
        )


class ReadNotificationSerializer(serializers.Serializer):
    """
    Serializer to read notifications
    """

    ids = fields.SerializableRelatedField(
        required=False, queryset=Notification.objects.all(), many=True)
    all = serializers.BooleanField(required=False, default=False)

    class Meta:
        fields = ('ids', 'all')

    def validate(self, attrs):
        if 'ids' in attrs and attrs['ids']:
            return attrs
        if 'all' in attrs and attrs['all']:
            return attrs
        raise serializers.ValidationError(
            _("Either 'ids' should be mentioned or 'all' should be True"))

    def create(self, validated_data):
        notifications = Notification.objects.all()
        if 'ids' in validated_data and validated_data['ids']:
            notifications = notifications.filter(id__in=validated_data['ids'])
        notifications.update(is_read=True)
        return {}

    def to_representation(self, instance):
        return instance

