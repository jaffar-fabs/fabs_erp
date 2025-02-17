from django.db import models
from django.utils.timezone import now
import uuid

class PaycycleMaster(models.Model):
    comp_code = models.CharField(max_length=20, null=False, blank=False)
    process_cycle_id = models.BigIntegerField(null=False, blank=False)
    process_cycle = models.CharField(null=False, blank=False)
    process_description = models.CharField(max_length=500, null=False, blank=False)
    pay_process_month = models.CharField(max_length=20, null=False, blank=False)
    date_from = models.DateField(null=False, blank=False)
    date_to = models.DateField(null=False, blank=False)
    process_date = models.DateField(null=True, blank=True)
    process_comp_flag = models.BigIntegerField(null=False, blank=False)
    hours_per_day = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    days_per_month = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    attendance_uom = models.BigIntegerField(null=False, blank=False)
    instance_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=False, blank=False)
    max_mn_hrs = models.IntegerField(null=True, blank=True)
    max_an_hrs = models.IntegerField(null=True, blank=True)
    max_ot1_hrs = models.IntegerField(null=True, blank=True)
    max_ot2_hrs = models.IntegerField(null=True, blank=True)
    ot1_amt = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    ot2_amt = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    travel_time = models.FloatField(null=True, blank=True)
    lunch_break = models.FloatField(null=True, blank=True)
    ot_eligible = models.CharField(max_length=1, null=True, blank=True)
    ot2_eligible = models.CharField(max_length=1, null=True, blank=True)
    default_project = models.CharField(max_length=30, null=True, blank=True)
    start_time = models.CharField(max_length=30, null=True, blank=True)
    end_time = models.CharField(max_length=30, null=True, blank=True)
    is_active = models.CharField(max_length=1, null=False,)
    created_by = models.BigIntegerField(null=False, blank=False)
    created_on = models.DateTimeField(default=now, null=False, blank=False)
    modified_by = models.BigIntegerField(null=True, blank=True)
    modified_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.comp_code


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


class UserMaster(models.Model):
    comp_code = models.CharField(max_length=15)
    user_master_id = models.BigIntegerField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    user_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    dob = models.DateField(blank=True, null=True)
    email = models.EmailField(max_length=50, unique=True)
    gender = models.BigIntegerField()
    is_active = models.BooleanField()
    instance_id = models.CharField(max_length=50)
    profile_picture = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.BigIntegerField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True)
    emp_code = models.CharField(max_length=20, blank=True, null=True)
    user_paycycles = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.user_id
    class Meta:
        db_table = 'tbl_erp_smas_user_master'