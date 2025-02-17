from django.db import models

class RoleMaster(models.Model):
    id = models.BigAutoField(primary_key=True)  
    comp_code = models.CharField(max_length=15)  
    role_name = models.CharField(max_length=50) 
    role_description = models.TextField()  
    created_by = models.BigIntegerField()  
    created_on = models.DateTimeField(auto_now_add=True)  
    modified_by = models.BigIntegerField(blank=True, null=True)  
    modified_on = models.DateTimeField(auto_now=True)  
    is_active = models.BooleanField()
    def __str__(self):
        return self.role_name  

    class Meta:
        db_table = 'tbl_erp_smas_role_master'