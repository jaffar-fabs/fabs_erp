from django.db import models

from django.db import models
import uuid

class projectMatster(models.Model):
    comp_code = models.CharField(max_length=15)
    project_id = models.BigAutoField(primary_key=True)
    prj_code = models.CharField(max_length=50)
    prj_name = models.CharField(max_length=50)
    project_description = models.TextField(max_length=500)
    project_type = models.BigIntegerField()
    project_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    timeline_from = models.CharField(max_length=200, null=True, blank=True)
    timeline_to = models.CharField(max_length=200, null=True, blank=True)
    prj_city = models.BigIntegerField()
    consultant = models.CharField(max_length=50, null=True, blank=True)
    main_contractor = models.CharField(max_length=50, null=True, blank=True)
    sub_contractor = models.CharField(max_length=50, null=True, blank=True)
    instance_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_by = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.BigIntegerField(null=True, blank=True)
    modified_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    

    def __str__(self):
        return self.prj_name
