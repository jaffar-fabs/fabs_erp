from django.db import models

# Create your models here.

from django.db import models

class ItemMaster(models.Model):
    id = models.AutoField(primary_key=True)
    item_code = models.CharField(max_length=100)
    item_description = models.CharField(max_length=500)
    remarks = models.CharField(max_length=500, blank=True, null=True)
    uom = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True) 
    created_by = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    comp_code = models.CharField(max_length=10)
    debactcd = models.CharField(max_length=20, blank=True, null=True)
    crdactcd = models.CharField(max_length=20, blank=True, null=True)
    vatactcd = models.CharField(max_length=20, blank=True, null=True)
    disactcd = models.CharField(max_length=20, blank=True, null=True)
    rndactcd = models.CharField(max_length=20, blank=True, null=True)
    item_type = models.CharField(max_length=100, blank=True, null=True)
    price_if_credit = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    stock_qty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    open_qty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    reorder_qty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    ord_by = models.IntegerField(blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    material = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=20, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    style = models.CharField(max_length=100, blank=True, null=True)
    origin = models.CharField(max_length=50, blank=True, null=True)
    sub_category = models.CharField(max_length=200, blank=True, null=True)
    intrcode = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    item_rate = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.item_code} - {self.item_description}"

class UOMMaster(models.Model):
    id = models.AutoField(primary_key=True)
    uom = models.CharField(max_length=200)
    seq = models.IntegerField(blank=True, null=True)
    base_uom = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    comp_code = models.CharField(max_length=10)

    def __str__(self):
        return self.uom

class WarehouseMaster(models.Model):
    id = models.AutoField(primary_key=True)
    comp_code = models.CharField(max_length=30)
    ware_code = models.CharField(max_length=30)
    ware_name = models.CharField(max_length=100)
    stat_code = models.CharField(max_length=30, default='A')
    ware_type = models.CharField(max_length=30, blank=True, null=True)
    created_by = models.CharField(max_length=30, default='SYSTEM')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=30, blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ware_code} - {self.ware_name}"

class PurchaseOrderHeader(models.Model):
    id = models.AutoField(primary_key=True)
    comp_code = models.CharField(max_length=30)
    tran_type = models.CharField(max_length=30)
    tran_date = models.DateField()
    tran_numb = models.CharField(max_length=30)
    supl_code = models.CharField(max_length=50)
    supl_name = models.CharField(max_length=100)
    supl_add1 = models.CharField(max_length=100, blank=True, null=True)
    supl_add2 = models.CharField(max_length=100, blank=True, null=True)
    supl_add3 = models.CharField(max_length=100, blank=True, null=True)
    cont_name = models.CharField(max_length=100, blank=True, null=True)
    mobl_numb = models.CharField(max_length=100, blank=True, null=True)
    teln_numb = models.CharField(max_length=100, blank=True, null=True)
    mail_addr = models.CharField(max_length=100, blank=True, null=True)
    refn_numb = models.CharField(max_length=100, blank=True, null=True)
    refn_date = models.DateField(blank=True, null=True)
    tran_remk = models.CharField(max_length=900, blank=True, null=True)
    totl_amnt = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    disc_prct = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    disc_amnt = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    taxx_prct = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    taxx_amnt = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    lpoo_amnt = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    prnt_flag = models.CharField(max_length=30, default='N')
    stat_code = models.CharField(max_length=30, default='ACT')
    created_by = models.CharField(max_length=30, default='SYSTEM')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=30, default='SYSTEM')
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tran_numb} - {self.supl_name}"

class PurchaseOrderDetail(models.Model):
    id = models.AutoField(primary_key=True)
    comp_code = models.CharField(max_length=30)
    tran_type = models.CharField(max_length=30)
    tran_date = models.DateField()
    tran_numb = models.CharField(max_length=30)
    tran_srno = models.IntegerField()
    item_code = models.CharField(max_length=100)
    item_desc = models.CharField(max_length=500, blank=True, null=True)
    item_unit = models.CharField(max_length=50)
    item_qnty = models.DecimalField(max_digits=18, decimal_places=2)
    item_rate = models.DecimalField(max_digits=18, decimal_places=2)
    item_disc = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    item_amnt = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    recv_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    item_taxx = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_by = models.CharField(max_length=30, default='SYSTEM')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=30, default='SYSTEM')
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tran_numb} - {self.item_code}"

class GRNHeader(models.Model):
    id = models.AutoField(primary_key=True)
    comp_code = models.CharField(max_length=30)
    tran_type = models.CharField(max_length=30)
    tran_date = models.DateField()
    tran_numb = models.CharField(max_length=30)
    ware_code = models.CharField(max_length=30)
    supl_code = models.CharField(max_length=50)
    lpoo_numb = models.CharField(max_length=100, blank=True, null=True)
    lpoo_date = models.DateField(blank=True, null=True)
    tran_remk = models.CharField(max_length=900, blank=True, null=True)
    stat_code = models.CharField(max_length=30, default='ACT')
    created_by = models.CharField(max_length=30, default='SYSTEM')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=30, default='SYSTEM')
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tran_numb} - {self.supl_code}"

class GRNDetail(models.Model):
    id = models.AutoField(primary_key=True)
    comp_code = models.CharField(max_length=30)
    tran_type = models.CharField(max_length=30)
    tran_date = models.DateField()
    tran_numb = models.CharField(max_length=30)
    tran_srno = models.IntegerField()
    ware_code = models.CharField(max_length=30)
    item_code = models.CharField(max_length=100)
    item_desc = models.CharField(max_length=500)
    item_unit = models.CharField(max_length=50)
    item_qnty = models.DecimalField(max_digits=18, decimal_places=2)
    created_by = models.CharField(max_length=30, default='SYSTEM')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=30, default='SYSTEM')
    updated_on = models.DateTimeField(auto_now=True)
    tran_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    item_in_pcs = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.tran_numb} - {self.item_code}"

class MaterialRequestHeader(models.Model):
    id = models.AutoField(primary_key=True)
    comp_code = models.CharField(max_length=20)
    ordr_type = models.CharField(max_length=50)
    ordr_date = models.DateField()
    ordr_numb = models.CharField(max_length=30)
    cust_code = models.CharField(max_length=40, null=True, blank=True)
    quot_stat = models.CharField(max_length=20, default='ACT')
    quot_numb = models.CharField(max_length=50, null=True, blank=True)
    quot_date = models.DateField(null=True, blank=True)
    quot_type = models.CharField(max_length=15, null=True, blank=True)
    ordr_disc = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    lpo_numb = models.CharField(max_length=50, null=True, blank=True)
    lpo_date = models.DateField(null=True, blank=True)
    services = models.CharField(max_length=30, null=True, blank=True)
    companys = models.CharField(max_length=30, null=True, blank=True)
    employee = models.CharField(max_length=30, null=True, blank=True)
    paym_mode = models.CharField(max_length=30, null=True, blank=True)
    totl_amnt = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    disc_amnt = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    vat_perct = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    vat_amnt = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    gtot_amnt = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_by = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=50, null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    old_flags = models.IntegerField(default=0)
    ordr_rvsn = models.IntegerField(default=0)
    job_code = models.CharField(max_length=50, null=True, blank=True)


class MaterialRequestDetail(models.Model):
    id = models.AutoField(primary_key=True)
    comp_code = models.CharField(max_length=20)
    ordr_type = models.CharField(max_length=50)
    ordr_date = models.DateField()
    ordr_numb = models.CharField(max_length=30)
    serl_numb = models.IntegerField()
    item_code = models.CharField(max_length=20)
    item_desc = models.CharField(max_length=500)
    item_unit = models.CharField(max_length=30)
    item_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    item_rate = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    item_amnt = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    mr_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    pr_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    bal = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    mreq_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    preq_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    miss_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    piss_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_by = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=50, null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class WarehouseHeader(models.Model):
    id_number = models.AutoField(primary_key=True)
    comp_code = models.CharField(max_length=30)
    ware_code = models.CharField(max_length=30)
    item_code = models.CharField(max_length=100)
    open_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    recv_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    issu_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    baln_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    stat_code = models.CharField(max_length=30)
    crte_user = models.CharField(max_length=30, default='SYSTEM')
    crte_date = models.DateTimeField(auto_now_add=True)
    updt_user = models.CharField(max_length=30, default='SYSTEM', null=True, blank=True)
    updt_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    item_luom = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        unique_together = ('comp_code', 'ware_code', 'item_code')

    def __str__(self):
        return f"{self.ware_code} - {self.item_code}"

class WarehouseDetail(models.Model):
    id_number = models.AutoField(primary_key=True)
    comp_code = models.CharField(max_length=30)
    tran_type = models.CharField(max_length=30)
    tran_date = models.DateField(null=True, blank=True)
    tran_numb = models.CharField(max_length=30)
    tran_srno = models.IntegerField()
    ware_code = models.CharField(max_length=30)
    item_code = models.CharField(max_length=100)
    item_tran = models.CharField(max_length=30)
    tran_qnty = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    refn_type = models.CharField(max_length=30, null=True, blank=True)
    refn_date = models.DateField(null=True, blank=True)
    refn_numb = models.CharField(max_length=30, null=True, blank=True)
    refn_srno = models.IntegerField(null=True, blank=True)
    tran_ware = models.CharField(max_length=30, null=True, blank=True)
    crte_user = models.CharField(max_length=30, default='SYSTEM')
    crte_date = models.DateTimeField(auto_now_add=True)
    updt_user = models.CharField(max_length=30, default='SYSTEM', null=True, blank=True)
    updt_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    item_luom = models.CharField(max_length=30, null=True, blank=True)
    slor_type = models.CharField(max_length=30, null=True, blank=True)
    slor_numb = models.CharField(max_length=50, null=True, blank=True)
    slor_date = models.DateField(null=True, blank=True)

    class Meta:        
        unique_together = ('comp_code', 'tran_type', 'tran_date', 'tran_numb', 'tran_srno')

    def __str__(self):
        return f"{self.tran_numb} - {self.item_code}"
