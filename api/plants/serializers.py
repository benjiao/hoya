from rest_framework import serializers
from django.urls import reverse
from .models import Location, Plant, PlantImage, PlantCareLog


class LocationSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()
    parent_id = serializers.PrimaryKeyRelatedField(
        source='parent',
        queryset=Location.objects.none(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    path_names = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    children_url = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = [
            'id', 'name', 'parent', 'parent_id',
            'path_names', 'display_name',
            'children_url', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['parent_id'].queryset = Location.objects.filter(user=request.user)

    def get_parent(self, obj):
        if obj.parent_id is None:
            return None
        return {'id': obj.parent.id, 'name': obj.parent.name}

    def get_children_url(self, obj):
        request = self.context.get('request')
        url = reverse('location-list') + f'?parent={obj.pk}'
        return request.build_absolute_uri(url) if request else url


class PlantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantImage
        fields = ['id', 'image', 'caption', 'uploaded_at']
        read_only_fields = ['uploaded_at']


class PlantCareLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantCareLog
        fields = ['id', 'type', 'notes', 'logged_at', 'created_at']
        read_only_fields = ['created_at']


class PlantSerializer(serializers.ModelSerializer):
    images = PlantImageSerializer(many=True, read_only=True)
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        source='location',
        queryset=Location.objects.none(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Plant
        fields = [
            'id', 'name', 'scientific_name',
            'location', 'location_id',
            'images', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['location_id'].queryset = Location.objects.filter(user=request.user)


class PlantListSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True, default=None)
    location_display_name = serializers.SerializerMethodField()
    location_path_names = serializers.SerializerMethodField()
    last_watered = serializers.DateTimeField(read_only=True, allow_null=True)
    last_repotted = serializers.DateTimeField(read_only=True, allow_null=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Plant
        fields = [
            'id', 'name', 'scientific_name',
            'location_name', 'location_display_name', 'location_path_names',
            'last_watered', 'last_repotted',
            'thumbnail',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_thumbnail(self, obj):
        first = obj.images.order_by('uploaded_at').first()
        if not first:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(first.image.url) if request else first.image.url

    def get_location_display_name(self, obj):
        if obj.location_id is None:
            return None
        return obj.location.display_name

    def get_location_path_names(self, obj):
        if obj.location_id is None:
            return None
        return obj.location.path_names
