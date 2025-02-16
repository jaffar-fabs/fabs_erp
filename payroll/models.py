from django.db import models

# Create your models here.

from django.db import models

class CodeMaster(models.Model):
    comp_code = models.CharField(max_length=15, null=False)
    common_master_id = models.BigAutoField(primary_key=True)
    base_type = models.CharField(max_length=100, null=False)
    base_value = models.CharField(max_length=100, null=False)
    base_description = models.CharField(max_length=500, blank=True, null=True)
    sequence_id = models.IntegerField(null=False)
    instance_id = models.CharField(max_length=50, null=False)
    is_active = models.CharField(max_length=2, null=False)
    created_by = models.BigIntegerField(default=1, null=False)
    created_on = models.DateTimeField(auto_now_add=True, null=False)
    modified_by = models.BigIntegerField(default=1, null=True)
    modified_on = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.base_type} - {self.base_value}"