from django.db import models
from django.utils.timezone import now
from django.utils import timezone
import uuid
import os

def employee_document_path(instance, filename):
    # Construct the path using the employee's code
    return os.path.join('employee_documents', instance.emp_code, filename)

def company_logo_upload_path(instance, filename):
    safe_code = str(instance.company_code).replace(" ", "_").replace("/", "_")
    return os.path.join('company_logos', safe_code, filename)

class Employee(models.Model):
    comp_code = models.CharField(max_length=15)  # Removed default value
    employee_id = models.AutoField(primary_key=True)  # Primary key for the employee
    emp_code = models.CharField(max_length=50, blank=True, null=True)  # Employee code
    emp_name = models.CharField(max_length=100)  # Employee name (as per passport)
    surname = models.CharField(max_length=50, blank=True, null=True)  # Surname
    dob = models.DateField(blank=True, null=True)  # Date of birth
    emp_sex = models.CharField(max_length=1, choices=[('1', 'Male'), ('2', 'Female')], default='1')  # Gender
    emp_status = models.CharField(max_length=50, blank=True, null=True)  # Employment status
    father_name = models.CharField(max_length=50, blank=True, null=True)  # Father's name
    mother_name = models.CharField(max_length=50, blank=True, null=True)  # Mother's name
    nationality = models.CharField(max_length=50, blank=True, null=True)  # Nationality
    religion = models.CharField(max_length=50, blank=True, null=True)  # Religion
    qualification = models.CharField(max_length=50, blank=True, null=True)  # Qualification
    emp_marital_status = models.CharField(max_length=150, blank=True, null=True)  # Marital status
    spouse_name = models.CharField(max_length=50, blank=True, null=True)  # Spouse's name
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Height in cm
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Weight in kg
    family_status = models.CharField(max_length=50, blank=True, null=True)  # Family status

    # Residential Address
    res_country_code = models.CharField(max_length=10, blank=True, null=True)  # Residential country code
    res_phone_no = models.CharField(max_length=20, blank=True, null=True)  # Residential phone number
    res_addr_line1 = models.CharField(max_length=100, blank=True, null=True)  # Residential address line 1
    res_addr_line2 = models.CharField(max_length=100, blank=True, null=True)  # Residential address line 2
    res_city = models.CharField(max_length=50, blank=True, null=True)  # Residential city
    res_state = models.CharField(max_length=50, blank=True, null=True)  # Residential state

    # Local Residence
    local_country_code = models.CharField(max_length=10, blank=True, null=True)  # Local country code
    local_phone_no = models.CharField(max_length=20, blank=True, null=True)  # Local phone number
    local_addr_line1 = models.CharField(max_length=100, blank=True, null=True)  # Local address line 1
    local_addr_line2 = models.CharField(max_length=100, blank=True, null=True)  # Local address line 2
    local_city = models.CharField(max_length=50, blank=True, null=True)  # Residential city
    local_state = models.CharField(max_length=50, blank=True, null=True)  # Residential state

    # Payment Details
    labour_id = models.CharField(max_length=50, blank=True, null=True)  # Labour ID
    process_cycle = models.CharField(max_length=50, blank=True, null=True)  # Payment process cycle
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2)  # Basic pay
    allowance = models.DecimalField(max_digits=10, decimal_places=2)  # Allowance
    grade_code = models.CharField(max_length=150, blank=True, null=True)  # Grade code
    designation = models.CharField(max_length=50, blank=True, null=True)  # Designation
    department = models.CharField(max_length=50, blank=True, null=True)  # Department
    date_of_join = models.DateField(blank=True, null=True)  # Date of joining
    date_of_rejoin = models.DateField(blank=True, null=True)  # Date of rejoining
    depend_count = models.IntegerField(blank=True, null=True)  # Dependent count
    child_count = models.IntegerField(blank=True, null=True)  # Child count

    # Account Details
    employee_bank = models.CharField(max_length=100, blank=True, null=True)  # Employee bank
    bank_branch = models.CharField(max_length=100, blank=True, null=True)  # Bank branch
    account_no = models.CharField(max_length=20, blank=True, null=True)  # Account number
    bank_loan = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Bank loan

    # Travel Document Details
    passport_document = models.FileField(upload_to=employee_document_path, blank=True, null=True)  # Passport document upload
    passport_details = models.CharField(max_length=100, blank=True, null=True)  # Passport details
    issued_date = models.DateField(blank=True, null=True)  # Issued date
    expiry_date = models.DateField(blank=True, null=True)  # Expiry date

    # New fields for Visa Details
    visa_no = models.CharField(max_length=50, blank=True, null=True)  # Visa number
    visa_issued = models.DateField(blank=True, null=True)  # Visa issued date
    visa_expiry = models.DateField(blank=True, null=True)  # Visa expiry date
    emirates_no = models.CharField(max_length=50, blank=True, null=True)  # Visa number
    emirate_issued = models.DateField(blank=True, null=True)  # Emirate issued
    emirate_expiry = models.DateField(blank=True, null=True)  # Emirate expiry date
    uid_number = models.CharField(max_length=50, blank=True, null=True)  # UID number
    mohra_number = models.CharField(max_length=50, blank=True, null=True)  # Mohra number
    work_permit_number = models.CharField(max_length=50, blank=True, null=True)  # Work permit number
    work_permit_expiry = models.DateField(blank=True, null=True)  # Work permit expiry date
    visa_document = models.FileField(upload_to=employee_document_path, blank=True, null=True)  # Visa document upload
    emirate_document = models.FileField(upload_to=employee_document_path, blank=True, null=True)  # Emirate document upload
    work_permit_document = models.FileField(upload_to=employee_document_path, blank=True, null=True)  # Work permit document upload
    profile_picture = models.FileField(upload_to=employee_document_path, blank=True, null=True)  # Profile pictur
    spouse_visa_copy = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    dependent_emirates_id = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    dependent_passport = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    child_birth_certificate = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    # Document Uploads
    manpower_request_id = models.CharField(max_length=50, blank=True, null=True)
    manpower_request_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    interview_assessment_id = models.CharField(max_length=50, blank=True, null=True)
    interview_assessment_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    passport_copy_id = models.CharField(max_length=50, blank=True, null=True)
    passport_copy_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    photo_id = models.CharField(max_length=50, blank=True, null=True)
    photo_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    offer_letter_id = models.CharField(max_length=50, blank=True, null=True)
    offer_letter_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    nominee_form_id = models.CharField(max_length=50, blank=True, null=True)
    nominee_form_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    change_status_id = models.CharField(max_length=50, blank=True, null=True)
    change_status_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    visa_copy_id = models.CharField(max_length=50, blank=True, null=True)
    visa_copy_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    emirates_id_id = models.CharField(max_length=50, blank=True, null=True)
    emirates_id_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    labor_contract_id = models.CharField(max_length=50, blank=True, null=True)
    labor_contract_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    job_offer_id = models.CharField(max_length=50, blank=True, null=True)
    job_offer_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    salary_certificate_id = models.CharField(max_length=50, blank=True, null=True)
    salary_certificate_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    salary_transfer_letter_id = models.CharField(max_length=50, blank=True, null=True)
    salary_transfer_letter_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    increment_letter_id = models.CharField(max_length=50, blank=True, null=True)
    increment_letter_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    warning_letter_id = models.CharField(max_length=50, blank=True, null=True)
    warning_letter_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    experience_letter_id = models.CharField(max_length=50, blank=True, null=True)
    experience_letter_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    resignation_letter_id = models.CharField(max_length=50, blank=True, null=True)
    resignation_letter_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    termination_letter_id = models.CharField(max_length=50, blank=True, null=True)
    termination_letter_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    employee_confidential_form_id = models.CharField(max_length=50, blank=True, null=True)
    employee_confidential_form_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    leave_application_id = models.CharField(max_length=50, blank=True, null=True)
    leave_application_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)
    full_final_settlement_copy_id = models.CharField(max_length=50, blank=True, null=True)
    full_final_settlement_copy_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    # Fields with additional date inputs
    passport_issued_date = models.DateField(blank=True, null=True)
    passport_expiry_date = models.DateField(blank=True, null=True)
    visa_issued_date = models.DateField(blank=True, null=True)
    visa_expiry_date = models.DateField(blank=True, null=True)
    emirates_id_issued_date = models.DateField(blank=True, null=True)
    emirates_id_expiry_date = models.DateField(blank=True, null=True)
    labor_contract_issued_date = models.DateField(blank=True, null=True)
    labor_contract_expiry_date = models.DateField(blank=True, null=True)

    # Dependent Details
    father_visa_copy_id = models.CharField(max_length=50, blank=True, null=True)
    father_visa_copy_issued_date = models.DateField(blank=True, null=True)
    father_visa_copy_expiry_date = models.DateField(blank=True, null=True)
    father_visa_copy_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    father_emirates_id_id = models.CharField(max_length=50, blank=True, null=True)
    father_emirates_id_issued_date = models.DateField(blank=True, null=True)
    father_emirates_id_expiry_date = models.DateField(blank=True, null=True)
    father_emirates_id_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    father_passport_id = models.CharField(max_length=50, blank=True, null=True)
    father_passport_issued_date = models.DateField(blank=True, null=True)
    father_passport_expiry_date = models.DateField(blank=True, null=True)
    father_passport_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    mother_visa_copy_id = models.CharField(max_length=50, blank=True, null=True)
    mother_visa_copy_issued_date = models.DateField(blank=True, null=True)
    mother_visa_copy_expiry_date = models.DateField(blank=True, null=True)
    mother_visa_copy_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    mother_emirates_id_id = models.CharField(max_length=50, blank=True, null=True)
    mother_emirates_id_issued_date = models.DateField(blank=True, null=True)
    mother_emirates_id_expiry_date = models.DateField(blank=True, null=True)
    mother_emirates_id_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    mother_passport_id = models.CharField(max_length=50, blank=True, null=True)
    mother_passport_issued_date = models.DateField(blank=True, null=True)
    mother_passport_expiry_date = models.DateField(blank=True, null=True)
    mother_passport_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    spouse_visa_copy_id = models.CharField(max_length=50, blank=True, null=True)
    spouse_visa_copy_issued_date = models.DateField(blank=True, null=True)
    spouse_visa_copy_expiry_date = models.DateField(blank=True, null=True)
    spouse_visa_copy_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    spouse_emirates_id_id = models.CharField(max_length=50, blank=True, null=True)
    spouse_emirates_id_issued_date = models.DateField(blank=True, null=True)
    spouse_emirates_id_expiry_date = models.DateField(blank=True, null=True)
    spouse_emirates_id_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    spouse_passport_id = models.CharField(max_length=50, blank=True, null=True)
    spouse_passport_issued_date = models.DateField(blank=True, null=True)
    spouse_passport_expiry_date = models.DateField(blank=True, null=True)
    spouse_passport_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    child1_visa_copy_id = models.CharField(max_length=50, blank=True, null=True)
    child1_visa_copy_issued_date = models.DateField(blank=True, null=True)
    child1_visa_copy_expiry_date = models.DateField(blank=True, null=True)
    child1_visa_copy_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    child1_emirates_id_id = models.CharField(max_length=50, blank=True, null=True)
    child1_emirates_id_issued_date = models.DateField(blank=True, null=True)
    child1_emirates_id_expiry_date = models.DateField(blank=True, null=True)
    child1_emirates_id_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    child1_passport_id = models.CharField(max_length=50, blank=True, null=True)
    child1_passport_issued_date = models.DateField(blank=True, null=True)
    child1_passport_expiry_date = models.DateField(blank=True, null=True)
    child1_passport_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    child1_birth_certificate_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    child2_visa_copy_id = models.CharField(max_length=50, blank=True, null=True)
    child2_visa_copy_issued_date = models.DateField(blank=True, null=True)
    child2_visa_copy_expiry_date = models.DateField(blank=True, null=True)
    child2_visa_copy_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    child2_emirates_id_id = models.CharField(max_length=50, blank=True, null=True)
    child2_emirates_id_issued_date = models.DateField(blank=True, null=True)
    child2_emirates_id_expiry_date = models.DateField(blank=True, null=True)
    child2_emirates_id_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    child2_passport_id = models.CharField(max_length=50, blank=True, null=True)
    child2_passport_issued_date = models.DateField(blank=True, null=True)
    child2_passport_expiry_date = models.DateField(blank=True, null=True)
    child2_passport_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    child2_birth_certificate_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    child3_visa_copy_id = models.CharField(max_length=50, blank=True, null=True)
    child3_visa_copy_issued_date = models.DateField(blank=True, null=True)
    child3_visa_copy_expiry_date = models.DateField(blank=True, null=True)
    child3_visa_copy_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    child3_emirates_id_id = models.CharField(max_length=50, blank=True, null=True)
    child3_emirates_id_issued_date = models.DateField(blank=True, null=True)
    child3_emirates_id_expiry_date = models.DateField(blank=True, null=True)
    child3_emirates_id_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    child3_passport_id = models.CharField(max_length=50, blank=True, null=True)
    child3_passport_issued_date = models.DateField(blank=True, null=True)
    child3_passport_expiry_date = models.DateField(blank=True, null=True)
    child3_passport_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    child3_birth_certificate_file = models.FileField(upload_to=employee_document_path, blank=True, null=True)

    # Audit Fields
    created_by = models.BigIntegerField(default=1)  # Created by
    modified_by = models.BigIntegerField(null=True, blank=True)  # Modified by
    created_on = models.DateTimeField(auto_now_add=True, null=True)  # Created on
    modified_on = models.DateTimeField(auto_now=True, null=True)  # Modified on

    def __str__(self):
        return f"{self.emp_name} ({self.emp_code})"
    
# ------------------------------------------------------------------------------------------------------------
class EarnDeductMaster(models.Model):
    comp_code = models.CharField(max_length=15)
    earndeduct_id = models.BigAutoField(primary_key=True)
    employee_code = models.CharField(max_length=15)
    earn_deduct_code = models.CharField(max_length=15)
    earn_deduct_amt = models.DecimalField(max_digits=18, decimal_places=2)
    prorated_flag = models.BooleanField()
    is_active = models.BooleanField(default=True)
    created_by = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.BigIntegerField(null=True, blank=True)
    modified_on = models.DateTimeField(null=True, blank=True)
    instance_id = models.CharField(max_length=50)
    earn_type = models.CharField(max_length=15, null=True, blank=True)


# ------------------------------------------------------------------------------------------------------------

# Role Menu Mapping

class RoleMenu(models.Model):
        
    comp_code = models.CharField(max_length=15)  # Removed default value
    role_id = models.PositiveBigIntegerField()  # Correct field name
    menu_id = models.PositiveBigIntegerField()
    mapping_id = models.AutoField(primary_key=True)
    add = models.BooleanField(null=True, blank=True)
    view = models.BooleanField(null=True, blank=True)
    delete = models.BooleanField(null=True, blank=True)
    modify = models.BooleanField(null=True, blank=True)
    instance_id = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.BigIntegerField(null=True, blank=True)
    modified_on = models.DateTimeField(null=True, blank=True)
    execute = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Mapping {self.mapping_id} - Role {self.role_id} - Menu {self.menu_id}"


# ------------------------------------------------------------------------------------------------------------

# PayCycle Master 

class PaycycleMaster(models.Model):

    comp_code = models.CharField(max_length=20)  # Removed default value
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
    comp_code = models.CharField(max_length=15)  # Removed default value
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

    comp_code = models.CharField(max_length=15)  # Removed default value
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

    comp_code = models.CharField(max_length=15, null=False)  # Removed default value
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

    comp_code = models.CharField(max_length=15)  # Removed default value
    user_master_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    user_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    dob = models.DateField(blank=True, null=True)
    email = models.EmailField(max_length=50, unique=True)
    gender = models.CharField(max_length=150, null=True)
    is_active = models.BooleanField()
    instance_id = models.CharField(max_length=50, null=True)
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

    comp_code = models.CharField(max_length=10)  # Removed default value
    grade_id = models.AutoField(primary_key=True)
    grade_code = models.CharField(max_length=20, unique=True)
    grade_desc = models.TextField(default="N/A")
    nationality = models.CharField(max_length=50, null=True)
    attendance_days = models.IntegerField(default=0, null=True)
    leave_days = models.IntegerField(default=0, null=True)
    passage_amount_adult = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    passage_amount_child = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    allowance1 = models.CharField(max_length=20 , null=True)
    allowance2 = models.CharField(max_length=20 , null=True)
    allowance3 = models.CharField(max_length=20 , null=True)
    allowance4 = models.CharField(max_length=20 , null=True)
    allowance5 = models.CharField(max_length=20 , null=True)
    allowance6 = models.CharField(max_length=20 , null=True)
    allowance7 = models.CharField(max_length=20 , null=True)
    allowance8 = models.CharField(max_length=20 , null=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
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
    comp_code = models.CharField(max_length=10) 
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
        comp_code = models.CharField(max_length=50)  # Removed defau7lt value
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


#-----------------------------------
# Company Master


class CompanyMaster(models.Model):
    company_id = models.BigAutoField(primary_key=True)
    company_code = models.CharField(max_length=15)  # Removed default value
    company_name = models.CharField(max_length=100)
    company_status = models.CharField(max_length=5)
    inception_date = models.CharField(max_length=200)
    labour_ministry_id = models.CharField(max_length=50, blank=True, null=True)
    labour_bank_acc_no = models.CharField(max_length=50, blank=True, null=True)
    currency_code = models.CharField(max_length=5)
    address_line1 = models.CharField(max_length=50, blank=True, null=True)
    address_line2 = models.CharField(max_length=50, blank=True, null=True)
    address_line_city = models.CharField(max_length=50, blank=True, null=True)
    address_line_state = models.CharField(max_length=50, blank=True, null=True)
    country_code = models.CharField(max_length=20, blank=True, null=True)
    telephone1 = models.CharField(max_length=20, blank=True, null=True)
    telephone2 = models.CharField(max_length=20, blank=True, null=True)
    fax_number = models.CharField(max_length=20, blank=True, null=True)
    mail_id = models.CharField(max_length=40, blank=True, null=True)
    social_media_id = models.CharField(max_length=50, blank=True, null=True)
    instance_id = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.BigIntegerField(blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    image_url = models.ImageField(upload_to=company_logo_upload_path, blank=True, null=True)
    salary_roundoff = models.CharField(max_length=50, blank=True, null=True)
    logo_blob = models.BinaryField(blank=True, null=True)
    po_box = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.company_name

# ------------------------------------------------------------------------------------------------------------

# Worker Attendance Register

class WorkerAttendanceRegister(models.Model):
    comp_code = models.CharField(max_length=50)  # Removed default value
    unique_id = models.BigAutoField(primary_key=True)
    employee_code = models.CharField(max_length=50)
    pay_cycle = models.CharField(max_length=100)
    pay_process_month = models.CharField(max_length=50)
    project_code = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField()
    attendance_type = models.BigIntegerField()
    morning = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    afternoon = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    ot1 = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    ot2 = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.BigIntegerField(blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    in_time = models.CharField(max_length=20, blank=True, null=True)
    out_time = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.employee_code} - {self.date}"


# -----------------------------------------------------------------------------------------------------------------------------------------------------

class AdvanceMaster(models.Model):
    comp_code = models.CharField(max_length=15, default='1000')
    advance_id = models.AutoField(primary_key=True)
    emp_code = models.CharField(max_length=15)
    advance_code = models.CharField(max_length=50, blank=True, null=True)
    advance_reference = models.CharField(max_length=100, blank=True, null=True)
    reference_date = models.DateField()
    total_amt = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    instalment_amt = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    paid_amt = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    total_no_instalment = models.BigIntegerField(blank=True, null=True)
    balance_no_instalment = models.BigIntegerField(blank=True, null=True)
    repayment_from = models.DateField()
    next_repayment_date = models.DateField()
    default_count = models.BigIntegerField(blank=True, null=True)
    waiver_amt = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    waiver_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.BigIntegerField()
    created_on = models.DateField(default=timezone.now)
    modified_by = models.BigIntegerField(blank=True, null=True)
    modified_on = models.DateField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.comp_code
    

# -----------------------------------------------------------------------------------------------------------------------------------------------------

class PayrollEarnDeduct(models.Model):
    unique_id = models.BigAutoField(primary_key=True)  # Identity column
    comp_code = models.CharField(max_length=20, null=False)
    emp_code =models.CharField(max_length=20, null=False)
    pay_process_month = models.DateField(null=True, blank=True, default=None)
    pay_process_cycle = models.CharField(max_length=50, null=True, blank=True)
    earn_deduct_code = models.CharField(max_length=50, null=True, blank=True)
    earn_deduct_type = models.CharField(max_length=50, null=True, blank=True)
    pay_amount = models.DecimalField(max_digits=18, decimal_places=2, null=False)
    project_code = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)  # Number(1,0) converted to BooleanField
    created_by = models.BigIntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)  # Defaults to current timestamp
    modified_by = models.BigIntegerField(null=True, blank=True)
    modified_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.comp_code
    
# -----------------------------------------------------------------------------------------------------------------------------------------------------


