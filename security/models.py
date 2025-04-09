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


# class Menu(models.Model):

#     menu_id = models.BigAutoField(primary_key=True)
#     comp_code = models.CharField(max_length=10, default="1001")
#     menu_name = models.CharField(max_length=50)
#     quick_path = models.BigIntegerField()
#     screen_name = models.CharField(max_length=50, null=True, blank=True)
#     url = models.CharField(max_length=100, null=True, blank=True)
#     module_id = models.CharField(max_length=50, null=True, blank=True)
#     parent_menu_id = models.CharField(null=True, blank=True)  
#     display_order = models.BigIntegerField()
#     instance_id = models.CharField(max_length=50)
#     buffer1 = models.CharField(max_length=10, null=True, blank=True)
#     buffer2 = models.CharField(max_length=10, null=True, blank=True)
#     buffer3 = models.CharField(max_length=10, null=True, blank=True)
#     is_active = models.BooleanField(default=True)
#     created_by = models.BigIntegerField()
#     created_on = models.DateTimeField(auto_now_add=True) 
#     modified_by = models.BigIntegerField(null=True, blank=True)
#     modified_on = models.DateTimeField(auto_now=True)  
#     is_add = models.BooleanField(null=True, blank=True)
#     is_view = models.BooleanField(null=True, blank=True)
#     is_edit = models.BooleanField(null=True, blank=True)
#     is_delete = models.BooleanField(null=True, blank=True)
#     is_execute = models.IntegerField(null=True, blank=True)
#     app_id = models.IntegerField(null=True, blank=True)
#     icon = models.CharField(max_length=100, null=True, blank=True)

#     def _str_(self):
#         return self.comp_code
    

from django.db import models

class UserRoleMapping(models.Model):
    comp_code = models.CharField(max_length=15, null=False)
    mappingid = models.BigAutoField(primary_key=True)
    userid = models.BigIntegerField(null=False)
    roleid = models.BigIntegerField(null=False)
    role_start_date = models.DateField(blank=True, null=True)
    role_to_date = models.DateField(blank=True, null=True)
    instance_id = models.CharField(max_length=50, blank=True, null=True)
    is_default_role = models.BooleanField(blank=True, null=True)
    is_active = models.BooleanField(null=False)
    created_by = models.BigIntegerField(null=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.BigIntegerField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.comp_code} - {self.userid} - {self.roleid}"
    
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


# class Menu(models.Model):

#     menu_id = models.BigAutoField(primary_key=True)
#     comp_code = models.CharField(max_length=10, default="1001")
#     menu_name = models.CharField(max_length=50)
#     quick_path = models.BigIntegerField()
#     screen_name = models.CharField(max_length=50, null=True, blank=True)
#     url = models.CharField(max_length=100, null=True, blank=True)
#     module_id = models.CharField(max_length=50, null=True, blank=True)
#     parent_menu_id = models.CharField(null=True, blank=True)  
#     display_order = models.BigIntegerField()
#     instance_id = models.CharField(max_length=50)
#     buffer1 = models.CharField(max_length=10, null=True, blank=True)
#     buffer2 = models.CharField(max_length=10, null=True, blank=True)
#     buffer3 = models.CharField(max_length=10, null=True, blank=True)
#     is_active = models.BooleanField(default=True)
#     created_by = models.BigIntegerField()
#     created_on = models.DateTimeField(auto_now_add=True) 
#     modified_by = models.BigIntegerField(null=True, blank=True)
#     modified_on = models.DateTimeField(auto_now=True)  
#     is_add = models.BooleanField(null=True, blank=True)
#     is_view = models.BooleanField(null=True, blank=True)
#     is_edit = models.BooleanField(null=True, blank=True)
#     is_delete = models.BooleanField(null=True, blank=True)
#     is_execute = models.IntegerField(null=True, blank=True)
#     app_id = models.IntegerField(null=True, blank=True)
#     icon = models.CharField(max_length=100, null=True, blank=True)

#     def _str_(self):
#         return self.comp_code
    

from django.db import models

class UserRoleMapping(models.Model):
    comp_code = models.CharField(max_length=15, null=False)
    mappingid = models.BigAutoField(primary_key=True)
    userid = models.BigIntegerField(null=False)
    roleid = models.BigIntegerField(null=False)
    role_start_date = models.DateField(blank=True, null=True)
    role_to_date = models.DateField(blank=True, null=True)
    instance_id = models.CharField(max_length=50, blank=True, null=True)
    is_default_role = models.BooleanField(blank=True, null=True)
    is_active = models.BooleanField(null=False)
    created_by = models.BigIntegerField(null=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.BigIntegerField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.comp_code} - {self.userid} - {self.roleid}"
