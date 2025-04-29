from django.db import models
from django.utils.timezone import now
from django.utils import timezone
import uuid
import os

def employee_document_path(instance, filename):
    # Construct the path using the employee's code
    return os.path.join('employee_documents', instance.emp_code, filename)

def camp_document_path(instance, filename):
    # Construct the path using the camp's code
    return os.path.join('camp_documents', instance.camp_code, filename)

def company_logo_upload_path(instance, filename):
    safe_code = str(instance.company_code).replace(" ", "_").replace("/", "_")
    return os.path.join('company_logos', safe_code, filename)

def party_documents_path(instance, filename):
    # Construct the path using the party's customer code
    return os.path.join('party_documents', instance.customer_code, filename)

# -------------------------------------------------------------------------------
# Party Master
class PartyMaster(models.Model):
    comp_code = models.CharField(max_length=15, null=True)  # Removed default value
    party_id = models.BigAutoField(primary_key=True)
    customer_code = models.CharField(max_length=50, unique=True) 
    customer_name = models.CharField(max_length=50)
    trade_license = models.CharField(max_length=50, null=True, blank=True)
    physical_address = models.CharField(max_length=100, null=True, blank=True)
    po_box = models.CharField(max_length=50, null=True, blank=True)
    emirates = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    telephone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    contact_person = models.CharField(max_length=50, null=True, blank=True)
    contact_person_phone = models.CharField(max_length=50, null=True, blank=True)
    contact_person_email = models.EmailField(max_length=50, null=True, blank=True)
    tax_treatment = models.CharField(max_length=50, null=True, blank=True)
    vat_no = models.CharField(max_length=50, null=True, blank=True)
    currency = models.CharField(max_length=50, null=True, blank=True)
    payment_terms = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.BigIntegerField(null=True, blank=True)
    modified_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    party_type = models.CharField(max_length=50, null=True, blank=True)

class PartyDocuments (models.Model):
    comp_code = models.CharField(max_length=15, null=True)  # Removed default value
    party_document_id = models.BigAutoField(primary_key=True)
    customer_code = models.CharField(max_length=50)
    document_name = models.CharField(max_length=50)
    document_file = models.FileField(upload_to=party_documents_path, blank=True, null=True)

# -------------------------------------------------------------------------------
#Camp Master

class CampMaster(models.Model):
    comp_code = models.CharField(max_length=15)
    camp_id = models.BigAutoField(primary_key=True)
    camp_code = models.CharField(max_length=50)
    camp_name = models.CharField(max_length=50)
    camp_agent = models.CharField(max_length=50, null=True, blank=True)
    upload_document = models.FileField(upload_to=camp_document_path, blank=True, null=True)
    ejari_start_date = models.DateField(null=True, blank=True)
    ejari_end_date = models.DateField(null=True, blank=True)
    rental_contract_start_date = models.DateField(null=True, blank=True)
    rental_contract_end_date = models.DateField(null=True, blank=True)
    rental_agreement_start_date = models.DateField(null=True, blank=True)
    rental_agreement_end_date = models.DateField(null=True, blank=True)
    camp_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    cheque_details = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.BigIntegerField( null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.BigIntegerField(null=True, blank=True)
    modified_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)


class CampDetails(models.Model):
    comp_code = models.CharField(max_length=15) 
    camp_details_id = models.BigAutoField(primary_key=True)
    camp_code = models.CharField(max_length=50)
    block = models.CharField(max_length=50, null=True, blank=True)
    floor = models.CharField(max_length=50, null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    
    room_no = models.CharField(null=True, blank=True)  # renamed from no_of_rooms
    as_per_mohre = models.IntegerField(null=True, blank=True)
    allocated = models.IntegerField(null=True, blank=True)
    as_per_rental = models.IntegerField(null=True, blank=True)
    allocation_building = models.CharField(max_length=100, null=True, blank=True)
    
    lower_bed = models.IntegerField(null=True, blank=True)
    upper_bed = models.IntegerField(null=True, blank=True)
    total_beds = models.IntegerField(null=True, blank=True)
    occupied_beds = models.IntegerField(null=True, blank=True)
    available_beds = models.IntegerField(null=True, blank=True)

class CampBeds(models.Model):
    comp_code = models.CharField(max_length=15)
    camp_beds_id = models.BigAutoField(primary_key=True)
    camp_code = models.CharField(max_length=50)
    block = models.CharField(max_length=50, null=True, blank=True)
    floor = models.CharField(max_length=50, null=True, blank=True)
    room_no = models.IntegerField(null=True, blank=True)
    bed_no = models.CharField(null=True, blank=True)
    bed_status = models.CharField(max_length=50, null=True, blank=True)
    emp_code = models.CharField(max_length=50, null=True, blank=True)
    
class CampDocuments(models.Model):
    comp_code = models.CharField(max_length=15)
    camp_document_id = models.BigAutoField(primary_key=True)
    camp_code = models.CharField(max_length=50)
    document_name = models.CharField(max_length=50)
    document_file = models.FileField(upload_to=camp_document_path, blank=True, null=True)


class CampCheque(models.Model):
    comp_code = models.CharField(max_length=15)
    camp_cheque_id = models.BigAutoField(primary_key=True)
    camp_code = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=50, null=True, blank=True)
    cheque_no = models.CharField(max_length=50, null=True, blank=True)
    cheque_date = models.DateField(null=True, blank=True)
    cheque_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)


class CampAllocation(models.Model):
    comp_code = models.CharField(max_length=15)
    transaction_id = models.BigAutoField(primary_key=True)
    request_id = models.CharField(max_length=200, null=True, blank=True)
    action_type = models.CharField(max_length=50, null=True, blank=True)
    employee_code = models.CharField(max_length=50)
    employee_name = models.CharField(max_length=100, null=True, blank=True)
    camp = models.CharField(max_length=50, null=True, blank=True)
    building_name = models.CharField(max_length=50, null=True, blank=True)
    floor_no = models.CharField(max_length=50, null=True, blank=True)
    room_no = models.CharField(max_length=50, null=True, blank=True)
    bed_no = models.CharField(max_length=50, null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    operational_approval = models.CharField(max_length=50, null=True, blank=True)
    current_camp = models.CharField(max_length=50, null=True, blank=True)
    current_building = models.CharField(max_length=50, null=True, blank=True)
    current_floor_no = models.CharField(max_length=50, null=True, blank=True)
    current_room_no = models.CharField(max_length=50, null=True, blank=True)
    current_bed_no = models.CharField(max_length=50, null=True, blank=True)
    exit_date = models.DateField(null=True, blank=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now=True)
    modified_by = models.BigIntegerField(null=True, blank=True)
    modified_on = models.DateTimeField(auto_now=True)

# -------------------------------------------------------------------------------
# Leave Master
class LeaveMaster(models.Model):
    DAY_TYPE_CHOICES = [
        ('Calendar', 'Calendar Days'),
        ('Working', 'Working Days'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('Paid', 'Paid Leave'),
        ('Unpaid', 'Unpaid Leave'),
        ('Half Paid', 'Half Paid Leave'),
    ]

    FREQUENCY_CHOICES = [
        ('Monthly', 'Monthly'),
        ('Yearly', 'Yearly'),
        ('One-time', 'One-time'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('All', 'All Genders'),
    ]

    leave_code = models.CharField(max_length=20, unique=True)  # Unique leave code
    leave_description = models.TextField()  # Description of leave
    work_month = models.PositiveIntegerField()  # Number of work months required for eligibility
    eligible_days = models.PositiveIntegerField()  # Number of eligible leave days
    eligible_day_type = models.CharField(max_length=10, choices=DAY_TYPE_CHOICES)  # Calendar or Working Days
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)  # Paid, Unpaid, Half Paid
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)  # Monthly, Yearly, One-time
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='All')  # Gender eligibility
    grade = models.CharField(max_length=50, blank=True, null=True)  # Employee grade (if applicable)
    carry_forward = models.BooleanField(default=False)  # Can leave be carried forward?
    carry_forward_period = models.PositiveIntegerField(default=0, help_text="Months allowed for carry forward")  # Carry forward period in months
    encashment = models.BooleanField(default=False)  # Whether the leave can be encashed
    encashment_days = models.PositiveIntegerField(default=0, help_text="Number of days allowed for encashment")  # Encashment days

    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp on creation
    updated_at = models.DateTimeField(auto_now=True)  # Auto timestamp on update

    def __str__(self):
        return f"{self.leave_code} - {self.leave_description}"

# -------------------------------------------------------------------------------
#Payprocess

class PayProcess(models.Model):
    comp_code = models.CharField(max_length=15)  # Company Code
    pay_cycle = models.CharField(max_length=10)  # Payroll Cycle (e.g., Monthly, Biweekly)
    pay_month = models.CharField(max_length=50)  # Payroll Month (MMYYYY format)
    employee_code = models.CharField(max_length=50)  # Employee Identifier
    project_code = models.CharField(max_length=50, blank=True, null=True)  # Project Code (optional)
    earn_type = models.CharField(max_length=50)  # Earnings Type (Basic Pay, Overtime, etc.)
    earn_code = models.CharField(max_length=50)  # Earnings Code
    morning = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)  # Morning Shift Earnings
    afternoon = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)  # Afternoon Shift Earnings
    ot1 = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)  # Overtime 1
    ot2 = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)  # Overtime 2
    amount = models.DecimalField(max_digits=18, decimal_places=5, default=0.00000)  # Total Earnings
    earn_reports = models.CharField(max_length=50, blank=True, null=True)  # Earnings Report Classification

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when record is created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when record is updated

    def __str__(self):
            return f"{self.employee_code} - {self.pay_month} - {self.earn_type}"


#---------------------------------------------------------------------------------

class Employee(models.Model):
    comp_code = models.CharField(max_length=15)  # Removed default value
    employee_id = models.AutoField(primary_key=True)  # Primary key for the employee
    emp_code = models.CharField(max_length=50, blank=True, null=True)  # Employee code
    emp_name = models.CharField(max_length=100)  # Employee name (as per passport)
    surname = models.CharField(max_length=50, blank=True, null=True)  # Surname
    dob = models.DateField(blank=True, null=True)  # Date of birth
    emp_sex = models.CharField(max_length=1, choices=[('1', 'Male'), ('2', 'Female')], default='1')  # Gender
    emp_status = models.CharField(max_length=50, blank=True, null=True)  # Employment status
    emp_sub_status = models.CharField(max_length=50, blank=True, null=True)  # Sub employment status
    passport_release = models.CharField(max_length=10, blank=True, null=True)  # Yes or No
    release_reason = models.CharField(max_length=255, blank=True, null=True)  # Reason for passport release
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
    allowance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Allowance
    grade_code = models.CharField(max_length=150, blank=True, null=True)  # Grade code
    prj_code = models.CharField(max_length=50, blank=True, null=True)
    sub_location = models.CharField(max_length=50, blank=True, null=True)  # Sub-location
    designation = models.CharField(max_length=50, blank=True, null=True)  # Designation
    department = models.CharField(max_length=50, blank=True, null=True)  # Department
    date_of_join = models.DateField(blank=True, null=True)  # Date of joining
    date_of_rejoin = models.DateField(blank=True, null=True)  # Date of rejoining
    staff_category = models.CharField(max_length=50, blank=True, null=True)  # Staff category
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
    passport_place_of_issue = models.CharField(max_length=50, blank=True, null=True)  # Passport place of issue
    passport_issued_country = models.CharField(max_length=50, blank=True, null=True)  # Passport issued country
    issued_date = models.DateField(blank=True, null=True)  # Issued date
    expiry_date = models.DateField(blank=True, null=True)  # Expiry date

    # New fields for Visa Details
    visa_location = models.CharField(max_length=50, blank=True, null=True)  # Visa location
    visa_no = models.CharField(max_length=50, blank=True, null=True)  # Visa number
    visa_issued = models.DateField(blank=True, null=True)  # Visa issued date
    visa_expiry = models.DateField(blank=True, null=True)  # Visa expiry date
    visa_designation = models.CharField(max_length=50, blank=True, null=True)  # Visa designation
    visa_issued_emirate = models.CharField(max_length=50, blank=True, null=True)  # Visa issued emirate
    iloe_no = models.CharField(max_length=50, blank=True, null=True)  # ILOE number
    iloe_expiry = models.DateField(blank=True, null=True)  # ILOE expiry date
    iloe_document = models.FileField(upload_to=employee_document_path, blank=True, null=True)  # ILOE document upload
    emirates_no = models.CharField(max_length=50, blank=True, null=True)  # Visa number
    emirate_issued = models.DateField(blank=True, null=True)  # Emirate issued
    emirate_expiry = models.DateField(blank=True, null=True)  # Emirate expiry date
    uid_number = models.CharField(max_length=50, blank=True, null=True)  # UID number
    mohra_number = models.CharField(max_length=50, blank=True, null=True)  # Mohra number
    mohra_name = models.CharField(max_length=50, blank=True, null=True)  # Mohra name
    mohra_designation = models.CharField(max_length=50, blank=True, null=True)  # Mohra designation
    work_permit_number = models.CharField(max_length=50, blank=True, null=True)  # Work permit number
    work_permit_expiry = models.DateField(blank=True, null=True)  # Work permit expiry date
    visa_document = models.FileField(upload_to=employee_document_path, blank=True, null=True)  # Visa document upload
    emirate_document = models.FileField(upload_to=employee_document_path, blank=True, null=True)  # Emirate document upload
    work_permit_document = models.FileField(upload_to=employee_document_path, blank=True, null=True)  # Work permit document upload
    profile_picture = models.FileField(upload_to=employee_document_path, blank=True, null=True)  # Profile pictur

    # Fields with additional date inputs
    passport_issued_date = models.DateField(blank=True, null=True)
    passport_expiry_date = models.DateField(blank=True, null=True)
    visa_issued_date = models.DateField(blank=True, null=True)
    visa_expiry_date = models.DateField(blank=True, null=True)
    emirates_id_issued_date = models.DateField(blank=True, null=True)
    emirates_id_expiry_date = models.DateField(blank=True, null=True)
    labor_contract_issued_date = models.DateField(blank=True, null=True)
    labor_contract_expiry_date = models.DateField(blank=True, null=True)

    # Camp Details
    camp_type = models.CharField(
        max_length=50, 
        blank=True, 
        null=True
    )  # Type of accommodation
    camp_inside_outside = models.CharField(
        max_length=100, 
        blank=True, 
        null=True
    )  # Inside/Outside/In Camp
    select_camp = models.CharField(max_length=100, blank=True, null=True)  # Selected camp
    room_no = models.CharField(max_length=100, blank=True, null=True)  # Room number
    outside_location = models.CharField(max_length=100, blank=True, null=True)  # Outside location
    room_rent = models.CharField(max_length=100, blank=True, null=True)  # Room rent
    client_name = models.CharField(max_length=150, null=True,blank=True)
    client_location = models.CharField(max_length=150, null=True,blank=True)

    # Audit Fields
    created_by = models.BigIntegerField(default=1)  # Created by
    modified_by = models.BigIntegerField(null=True, blank=True)  # Modified by
    created_on = models.DateTimeField(auto_now_add=True, null=True)  # Created on
    modified_on = models.DateTimeField(auto_now=True, null=True)  # Modified on

    def __str__(self):
        return f"{self.emp_name} ({self.emp_code})"
    
# ------------------------------------------------------------------------------------------------------------

# Employee Document
class EmployeeDocument(models.Model):
    comp_code = models.CharField(max_length=15)  # Removed default value
    document_id = models.AutoField(primary_key=True)  # Primary key for the document
    emp_code = models.CharField(max_length=50)  # Employee code
    document_type = models.CharField(max_length=250)  # Document type
    document_file = models.FileField(upload_to=employee_document_path)  # Document file
    created_by = models.BigIntegerField(null=True, blank=True)  # Created by
    created_on = models.DateTimeField(auto_now_add=True)  # Created on
    modified_by = models.BigIntegerField(null=True, blank=True)  # Modified by
    modified_on = models.DateTimeField(auto_now=True, null=True)  # Modified on
    relationship = models.CharField(max_length=50,null=True,blank=True)
    issued_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    document_number = models.CharField(max_length=100, null = True, blank= True)
    staff_work_location = models.CharField(max_length=100, null=True, blank=True)
    emirates_issued_by = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.document_name} ({self.emp_code})"

class EmployeeRecruitmentDetails(models.Model):
    comp_code = models.CharField(max_length=15)  
    recruitment_id = models.AutoField(primary_key=True)  
    emp_code = models.CharField(max_length=50) 
    agent_or_reference = models.CharField(max_length=150, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    change_status = models.CharField(max_length=100, null=True, blank=True)
    recruitment_from = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(null=True, blank=True)

#------------------------------------------------------------------------------------------------------------
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
    seed_prefix = models.CharField(max_length=50, null=True, blank=True)
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

class projectMaster(models.Model):

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
    instance_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_by = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.BigIntegerField(null=True, blank=True)
    modified_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    service_type = models.CharField(max_length=500, null=True, blank=True)  
    service_category = models.CharField(max_length=500, null=True, blank=True)  
    pro_sub_location = models.CharField(max_length=500, null=True, blank=True)
    customer = models.CharField(max_length=500, null=True, blank=True)
    agreement_ref = models.CharField(max_length=500, null=True, blank=True)
    op_head = models.CharField(max_length=500, null=True, blank=True)
    manager = models.CharField(max_length=500, null=True, blank=True)
    commercial_manager = models.CharField(max_length=500, null=True, blank=True)
    procurement_user = models.CharField(max_length=500, null=True, blank=True)
    indent_user = models.CharField(max_length=500, null=True, blank=True)
    final_contract_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    project_status = models.CharField(max_length=50, null=True, blank=True)

    
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
    

class CompanyDocument(models.Model):
    company_id = models.BigAutoField(primary_key=True)
    company_code = models.CharField(max_length=50)  # Removed default value
    document_type = models.CharField(max_length=50)
    document_number = models.CharField(max_length=50)
    issued_by = models.CharField(max_length=50, blank=True, null=True)
    issued_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=50, blank=True, null=True)
    remarks = models.CharField(max_length=500, blank=True, null=True)
    document_file = models.FileField(upload_to=company_logo_upload_path)  # Document file
    created_by = models.BigIntegerField(null=True, blank=True)  # Created by
    created_on = models.DateTimeField(auto_now_add=True)  # Created on
    modified_by = models.BigIntegerField(null=True, blank=True)  # Modified by
    modified_on = models.DateTimeField(auto_now=True, null=True)  # Modified on

    def __str__(self):
        return f"{self.document_type} ({self.company_id})"

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
    pay_process_month = models.CharField(null=True, blank=True, default=None)
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

