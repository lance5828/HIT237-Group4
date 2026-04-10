from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import OrderingFilter

from .models import Species, Observation
from .serializers import SpeciesSerializer, ObservationSerializer


# -------------------------
# Species Views
# -------------------------

class SpeciesListView(generics.ListCreateAPIView):
    serializer_class = SpeciesSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [OrderingFilter]
    ordering_fields = ['name']  # change if your model has different fields

    def get_queryset(self):
        queryset = Species.objects.all()
        
        # Filtering by name
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

    def perform_create(self, serializer):
        # Optional: only works if your model has a user field
        serializer.save()


class SpeciesDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# -------------------------
# Observation Views
# -------------------------

class ObservationListView(generics.ListCreateAPIView):
    serializer_class = ObservationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [OrderingFilter]
    ordering_fields = ['id']  # change if you have date/time fields

    def get_queryset(self):
        queryset = Observation.objects.all()

        # Filter by species (assuming ForeignKey exists)
        species_id = self.request.query_params.get('species')
        if species_id:
            queryset = queryset.filter(species_id=species_id)

        # Optional: filter by date if your model has it
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(date=date)

        return queryset

    def perform_create(self, serializer):
        serializer.save()


class ObservationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]