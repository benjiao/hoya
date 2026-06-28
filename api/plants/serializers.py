from rest_framework import serializers
from django.urls import reverse
from .models import Location, Plant, PlantImage, PlantCareLog, PlantStatus


class PlantStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantStatus
        fields = ['id', 'name', 'collapse_in_list']


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
            'skip_watering',
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
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = PlantImage
        fields = ['id', 'image', 'thumbnail', 'caption', 'uploaded_at', 'taken_at']
        read_only_fields = ['uploaded_at', 'taken_at']

    def get_thumbnail(self, obj):
        request = self.context.get('request')
        url_field = obj.thumbnail if obj.thumbnail else obj.image
        return request.build_absolute_uri(url_field.url) if request else url_field.url


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
    status = PlantStatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        source='status',
        queryset=PlantStatus.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    thumbnail_image_id = serializers.PrimaryKeyRelatedField(
        source='thumbnail_image',
        queryset=PlantImage.objects.none(),
        required=False,
        allow_null=True,
    )
    last_watered = serializers.DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = Plant
        fields = [
            'id', 'name', 'scientific_name',
            'watering_interval_days', 'last_watered',
            'location', 'location_id',
            'status', 'status_id',
            'thumbnail_image_id',
            'images', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'watering_interval_days', 'last_watered']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['location_id'].queryset = Location.objects.filter(user=request.user)
            self.fields['thumbnail_image_id'].queryset = PlantImage.objects.filter(plant__user=request.user)


class PlantListSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True, default=None)
    location_display_name = serializers.SerializerMethodField()
    location_path_names = serializers.SerializerMethodField()
    location_skip_watering = serializers.BooleanField(source='location.skip_watering', read_only=True, default=False)
    last_watered = serializers.DateTimeField(read_only=True, allow_null=True)
    last_repotted = serializers.DateTimeField(read_only=True, allow_null=True)
    thumbnail = serializers.SerializerMethodField()
    full_image = serializers.SerializerMethodField()
    status_id = serializers.IntegerField(source='status.id', read_only=True, allow_null=True, default=None)
    status_name = serializers.CharField(source='status.name', read_only=True, allow_null=True, default=None)
    status_collapse_in_list = serializers.BooleanField(source='status.collapse_in_list', read_only=True, default=False)

    class Meta:
        model = Plant
        fields = [
            'id', 'name', 'scientific_name',
            'watering_interval_days',
            'location_name', 'location_display_name', 'location_path_names', 'location_skip_watering',
            'last_watered', 'last_repotted',
            'status_id', 'status_name', 'status_collapse_in_list',
            'thumbnail', 'full_image',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'watering_interval_days']

    def _resolve_thumbnail_image(self, obj):
        return obj.thumbnail_image if obj.thumbnail_image_id else obj.images.order_by('uploaded_at').first()

    def get_thumbnail(self, obj):
        img = self._resolve_thumbnail_image(obj)
        if not img:
            return None
        request = self.context.get('request')
        url_field = img.thumbnail if img.thumbnail else img.image
        return request.build_absolute_uri(url_field.url) if request else url_field.url

    def get_full_image(self, obj):
        img = self._resolve_thumbnail_image(obj)
        if not img:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(img.image.url) if request else img.image.url

    def get_location_display_name(self, obj):
        if obj.location_id is None:
            return None
        return obj.location.display_name

    def get_location_path_names(self, obj):
        if obj.location_id is None:
            return None
        return obj.location.path_names
