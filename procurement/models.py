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
