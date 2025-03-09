from django.db import models
from django.utils.timezone import now
import uuid

class Employee(models.Model):
        
    employee_id = models.AutoField(primary_key=True)
    earn_deduct_type = models.CharField(max_length=50, blank=True, null=True)
    earn_deduct_code = models.CharField(max_length=50, default='1')  
    payprocess_cycle = models.CharField(max_length=50,blank=True, null=True) 
    payprocess_month = models.CharField(max_length=50, default='1')  
    comp_code = models.CharField(max_length=20)
    emp_code = models.CharField(max_length=50,blank=True, null=True)
    labour_id = models.CharField(max_length=50, blank=True, null=True)
    labour_bank_acc_no = models.CharField(max_length=20, blank=True, null=True)
    emp_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=50, blank=True, null=True)
    mother_name = models.CharField(max_length=50, blank=True, null=True)
    spouse_name = models.CharField(max_length=50, blank=True, null=True)
    emp_sex = models.CharField(max_length=50, default='1')  
    emp_marital_status = models.CharField(max_length=50, default='1')  
    emp_status = models.CharField(max_length=50,blank=True, null=True)
    emp_type = models.BigIntegerField(null=True, blank=True)
    dep_code = models.CharField(max_length=50, default='1')  
    prj_code = models.CharField(max_length=50,blank=True, null=True)
    desig_code = models.CharField(max_length=50,blank=True, null=True)
    grade_code = models.CharField(max_length=50,blank=True, null=True)
    basic_pay = models.BigIntegerField()
    allowance = models.BigIntegerField()
    dob = models.DateField(blank=True, null=True)
    date_of_join = models.DateField(blank=True, null=True)
    date_of_rejoin = models.DateField(blank=True, null=True)
    process_cycle = models.CharField(max_length=50,blank=True, null=True)
    ot_type = models.CharField(max_length=50, blank=True, null=True)
    addrline1 = models.CharField(max_length=50, blank=True, null=True)
    addrline2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    phone_no = models.CharField(max_length=20, blank=True, null=True)
    country_code = models.CharField(max_length=50,blank=True, null=True)
    r_addrline1 = models.CharField(max_length=50, blank=True, null=True)
    r_addrline2 = models.CharField(max_length=50, blank=True, null=True)
    r_city = models.CharField(max_length=50, blank=True, null=True)
    r_state = models.CharField(max_length=50, blank=True, null=True)
    r_phone_no = models.CharField(max_length=20, blank=True, null=True)
    r_country_code = models.CharField(max_length=50)
    emp_bank = models.CharField(max_length=50, blank=True, null=True)
    emp_bank_branch = models.CharField(max_length=50, blank=True, null=True)
    emp_acc_no = models.BigIntegerField(null=True,blank=True)
    bank_loan = models.BigIntegerField(blank=True, null=True)
    atten_type = models.BigIntegerField(blank=True, null=True)
    pay_process_flag = models.IntegerField(blank=True, null=True)
    emp_height = models.CharField(max_length=50,blank=True, null=True)
    emp_weight = models.CharField(max_length=50,blank=True, null=True)
    depen_count = models.BigIntegerField(blank=True, null=True)
    child_count = models.BigIntegerField(blank=True, null=True)
    passport_no = models.CharField(max_length=50, blank=True, null=True)
    passport_issuedat = models.CharField(max_length=50, blank=True, null=True)
    passport_validity = models.DateField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)
    instance_id = models.CharField(max_length=50, default='NEWID()', null=True)
    created_on = models.DateField(auto_now_add=True, null=True)
    modified_on = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=50, default='1')
    family_status = models.CharField(max_length=50, default='1')
    qualification = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=50, default='1')
    amounts = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    email1 = models.CharField(max_length=150)
    email2 = models.CharField(max_length=150,blank=True, null=True)
    locn_code = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.BigIntegerField(default=1)
    modified_by = models.BigIntegerField(null=True, blank=True)

    def str(self):
        return self.emp_code

# ------------------------------------------------------------------------------------------------------------

# Role Menu Mapping

class RoleMenu(models.Model):
        
    comp_code = models.CharField(max_length=15, default='1000')
    role_id = models.PositiveBigIntegerField()  # Correct field name
    menu_id = models.PositiveBigIntegerField()
    mapping_id = models.AutoField(primary_key=True)
    add = models.BooleanField(null=True, blank=True)
    view = models.BooleanField(null=True, blank=True)
    delete = models.BooleanField(null=True, blank=True)
    modify = models.BooleanField(null=True, blank=True)
    instance_id = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_by = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.BigIntegerField(null=True, blank=True)
    modified_on = models.DateTimeField(null=True, blank=True)
    execute = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Mapping {self.mapping_id} - Role {self.role_id} - Menu {self.menu_id}"


# ------------------------------------------------------------------------------------------------------------

# PayCycle Master 

class PaycycleMaster(models.Model):

    comp_code = models.CharField(max_length=20, null=False, blank=False)
    process_cycle_id = models.BigIntegerField(null=False, blank=False)
    process_cycle = models.CharField(null=False, blank=False)
    process_description = models.CharField(max_length=500, null=False, blank=False)
    pay_process_month = models.CharField(max_length=20, null=False, blank=False)
    date_from = models.DateField(null=False, blank=False)
    date_to = models.DateField(null=False, blank=False)
    process_date = models.DateField(null=True, blank=True)
    process_comp_flag = models.CharField(max_length=20, null=False, blank=False)
    hours_per_day = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    days_per_month = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    attendance_uom = models.CharField(max_length=20, null=False, blank=False)
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

# ------------------------------------------------------------------------------------------------------------

# Seed Master 

from django.db import models

class SeedModel(models.Model):

    seed_id = models.BigAutoField(primary_key=True)
    comp_code = models.CharField(max_length=15, default='1000')  
    seed_code = models.CharField(max_length=50)
    seed_group = models.CharField(max_length=50)
    seed_type = models.CharField(max_length=50)
    seed_prefix = models.CharField(max_length=50)
    seed_length = models.BigIntegerField()
    seed_start_num = models.BigIntegerField()
    seed_next_num = models.BigIntegerField()
    seed_timeline_from = models.DateField()
    seed_timeline_to = models.DateField()
    seed_inc_by = models.BigIntegerField()
    is_active = models.BooleanField(default=True)
    created_by = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.BigIntegerField()
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payroll_seedmaster'  

    def __str__(self):
        return f"{self.seed_code} - {self.seed_group}"

# ------------------------------------------------------------------------------------------------------------

# Project Master 

class projectMatster(models.Model):

    comp_code = models.CharField(max_length=15)
    project_id = models.BigAutoField(primary_key=True)
    prj_code = models.CharField(max_length=50)
    prj_name = models.CharField(max_length=50)
    project_description = models.TextField(max_length=500)
    project_type = models.CharField(max_length=50, null=True, blank=True)
    project_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    timeline_from = models.DateField(null=False, blank=False)
    timeline_to = models.DateField(null=False, blank=False)
    prj_city = models.CharField(max_length=50, null=True, blank=True)
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
    
# ------------------------------------------------------------------------------------------------------------

# Code Master 

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

# ------------------------------------------------------------------------------------------------------------

# User  Master 

class UserMaster(models.Model):

    comp_code = models.CharField(max_length=15)
    user_master_id = models.AutoField(primary_key=True)
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
        
# ------------------------------------------------------------------------------------------------------------

# Grade Master 

class GradeMaster(models.Model):

    comp_code = models.CharField(max_length=10)
    grade_id = models.AutoField(primary_key=True)
    grade_code = models.CharField(max_length=20, unique=True)
    grade_desc = models.TextField(default="N/A")
    nationality = models.CharField(max_length=50)
    attendance_days = models.IntegerField(default=0)
    leave_days = models.IntegerField(default=0)
    passage_amount_adult = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    passage_amount_child = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    allowance1 = models.CharField(max_length=20)
    allowance2 = models.CharField(max_length=20)
    allowance3 = models.CharField(max_length=20)
    allowance4 = models.CharField(max_length=20)
    allowance5 = models.CharField(max_length=20)
    allowance6 = models.CharField(max_length=20)
    allowance7 = models.CharField(max_length=20)
    allowance8 = models.CharField(max_length=20)
    is_active = models.CharField(max_length=1)
    instance_id = models.CharField(max_length=50)
    created_by = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.grade_code
    
# ------------------------------------------------------------------------------------------------------------

# Menu Master 

class Menu(models.Model):

    menu_id = models.BigAutoField(primary_key=True)
    comp_code = models.CharField(max_length=10, default="1001")
    menu_name = models.CharField(max_length=50)
    quick_path = models.BigIntegerField()
    screen_name = models.CharField(max_length=50, null=True, blank=True)
    url = models.CharField(max_length=100, null=True, blank=True)
    module_id = models.CharField(max_length=50, null=True, blank=True)
    parent_menu_id = models.CharField(null=True, blank=True)  
    display_order = models.BigIntegerField()
    instance_id = models.CharField(max_length=50)
    buffer1 = models.CharField(max_length=10, null=True, blank=True)
    buffer2 = models.CharField(max_length=10, null=True, blank=True)
    buffer3 = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True) 
    modified_by = models.BigIntegerField(null=True, blank=True)
    modified_on = models.DateTimeField(auto_now=True)  
    is_add = models.BooleanField(null=True, blank=True)
    is_view = models.BooleanField(null=True, blank=True)
    is_edit = models.BooleanField(null=True, blank=True)
    is_delete = models.BooleanField(null=True, blank=True)
    is_execute = models.IntegerField(null=True, blank=True)
    app_id = models.IntegerField(null=True, blank=True)
    icon = models.CharField(max_length=100, null=True, blank=True)

    def _str_(self):
        return self.comp_code
    
# ------------------------------------------------------------------------------------------------------------

# Holiday Master

class HolidayMaster(models.Model):
        comp_code = models.CharField(max_length=50)
        unique_id = models.BigAutoField(primary_key=True)
        holiday = models.CharField(max_length=50, blank=True, null=True)
        holiday_type = models.CharField(max_length=50, blank=True, null=True)
        holiday_date = models.DateField()
        holiday_day = models.CharField(max_length=50)
        holiday_description = models.CharField(max_length=300)
        is_active = models.BooleanField(default=True)
        created_by = models.BigIntegerField()
        created_on = models.DateTimeField(auto_now_add=True)
        modified_by = models.BigIntegerField(blank=True, null=True)
        modified_on = models.DateTimeField(blank=True, null=True)

        def __str__(self):
            return f"{self.holiday} ({self.holiday_date})"
