from .models import Connection, Source
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import ConnectionSerializer, OrganizationSerializer, SourceSerializer
from rest_framework.permissions import IsAuthenticated
from api.models import Organization
from rest_framework import viewsets
from api.utils.crypt import cipher_suite
from rest_framework.response import Response
from rest_framework import status


class Sources(ListCreateAPIView):
    """List all sources / create a new source."""
    permission_classes = [IsAuthenticated]
    queryset = Source.objects.all().select_related('connection').order_by('-created_at')
    serializer_class = SourceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        file_path = validated_data['file_path']
        connection = validated_data.get('connection')
        if not connection:
            return Response({'error': 'A connection is required'}, status=status.HTTP_400_BAD_REQUEST)
        existing_sources = Source.objects.filter(file_path=file_path, connection=connection)
        if existing_sources.exists():
            return Response({'error': 'Source with similar details exists'}, status=status.HTTP_409_CONFLICT)

        source = Source.objects.create(**validated_data)
        return Response(SourceSerializer(source).data, status=status.HTTP_201_CREATED)


class SourceDetail(RetrieveUpdateDestroyAPIView):
    """Retrieve / edit (incl. file_path) / disable / delete a single source."""
    permission_classes = [IsAuthenticated]
    queryset = Source.objects.all().select_related('connection')
    serializer_class = SourceSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(SourceSerializer(instance).data)


class Connections(ListCreateAPIView):
    """List all connections / create a new connection (password is encrypted)."""
    permission_classes = [IsAuthenticated]
    queryset = Connection.objects.all().order_by('-created_at')
    serializer_class = ConnectionSerializer

    def create(self, request, *args, **kwargs):
        ssh_pass = request.data.get('ssh_pass')
        ssh_user = request.data.get('ssh_user')
        ssh_host = request.data.get('ssh_host')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not ssh_pass:
            return Response({'error': 'ssh password is required'}, status=status.HTTP_400_BAD_REQUEST)

        # no host should have the same password & username
        existing_connections = Connection.objects.filter(ssh_host=ssh_host, ssh_user=ssh_user)
        if existing_connections.exists():
            return Response({'error': 'Connection exists!'}, status=status.HTTP_409_CONFLICT)

        instance = serializer.save()
        instance.ssh_pass = cipher_suite().encrypt(ssh_pass.encode())
        instance.save(update_fields=['ssh_pass'])
        return Response(ConnectionSerializer(instance).data, status=status.HTTP_201_CREATED)


class ConnectionDetail(RetrieveUpdateDestroyAPIView):
    """Retrieve / edit / disable / delete a single connection. The ssh password is
    only re-encrypted and stored when a new (non-empty) value is supplied."""
    permission_classes = [IsAuthenticated]
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        ssh_pass = request.data.get('ssh_pass')
        if ssh_pass:
            instance.ssh_pass = cipher_suite().encrypt(ssh_pass.encode())
            instance.save(update_fields=['ssh_pass'])

        return Response(ConnectionSerializer(instance).data)


class OrganizationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
