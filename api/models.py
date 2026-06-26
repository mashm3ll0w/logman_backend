from django.db import models
from uuid import uuid4


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=30)
    code = models.CharField(max_length=30, unique=True, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class Connection(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    ssh_user = models.CharField(max_length=30)
    ssh_pass = models.BinaryField(blank=False)
    ssh_host = models.CharField(max_length=30)
    ssh_port = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ssh_host


class Source(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=30)
    file_path= models.CharField(max_length=100, blank=False, null=False)
    connection  = models.ForeignKey(Connection,on_delete=models.CASCADE, related_name='connections',)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    




