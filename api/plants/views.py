from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import OuterRef, Subquery

from .forms import LOCATION_SELECT_RELATED
from .models import Location, Plant, PlantImage, PlantCareLog
from .serializers import (
    LocationSerializer, PlantSerializer, PlantListSerializer,
    PlantImageSerializer, PlantCareLogSerializer,
)


class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer

    def get_queryset(self):
        qs = Location.objects.filter(user=self.request.user).select_related(
            *LOCATION_SELECT_RELATED,
        )
        parent_param = self.request.query_params.get('parent')
        if parent_param is not None:
            qs = qs.filter(parent=None if parent_param == 'null' else parent_param)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        locations = sorted(queryset, key=lambda loc: loc.path_names)
        serializer = self.get_serializer(locations, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PlantViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        last_watered = Subquery(
            PlantCareLog.objects.filter(plant=OuterRef('pk'), type='watered')
            .order_by('-logged_at').values('logged_at')[:1]
        )
        last_repotted = Subquery(
            PlantCareLog.objects.filter(plant=OuterRef('pk'), type='repotted')
            .order_by('-logged_at').values('logged_at')[:1]
        )
        return (
            Plant.objects.filter(user=self.request.user)
            .select_related(
                'location',
                'location__parent',
                'location__parent__parent',
                'location__parent__parent__parent',
                'thumbnail_image',
            )
            .annotate(last_watered=last_watered, last_repotted=last_repotted)
            .order_by('name')
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return PlantListSerializer
        return PlantSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get', 'post'], url_path='images',
            parser_classes=[MultiPartParser, FormParser])
    def images(self, request, pk=None):
        plant = self.get_object()
        ctx = {'request': request}
        if request.method == 'POST':
            serializer = PlantImageSerializer(data=request.data, context=ctx)
            serializer.is_valid(raise_exception=True)
            image = serializer.save(plant=plant)
            plant.thumbnail_image = image
            plant.save(update_fields=['thumbnail_image'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        serializer = PlantImageSerializer(plant.images.all(), many=True, context=ctx)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], url_path=r'images/(?P<image_pk>[^/.]+)')
    def image_detail(self, request, pk=None, image_pk=None):
        plant = self.get_object()
        try:
            image = plant.images.get(pk=image_pk)
        except PlantImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get', 'post'], url_path='logs')
    def logs(self, request, pk=None):
        plant = self.get_object()
        if request.method == 'POST':
            serializer = PlantCareLogSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(plant=plant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        serializer = PlantCareLogSerializer(
            plant.care_logs.order_by('-logged_at'), many=True
        )
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'put', 'patch', 'delete'],
            url_path=r'logs/(?P<log_pk>[^/.]+)')
    def log_detail(self, request, pk=None, log_pk=None):
        plant = self.get_object()
        try:
            log = plant.care_logs.get(pk=log_pk)
        except PlantCareLog.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            log.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        partial = request.method == 'PATCH'
        serializer = PlantCareLogSerializer(log, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
