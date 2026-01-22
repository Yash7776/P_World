class MasterProduct(models.Model):  # Admin's templates
    item_name = models.CharField(max_length = 200 , blank = True , null = True)
    item_price = models.FloatField(blank = True , null = True, default=0)
    fk_category = models.ForeignKey(ItemCategoryMaster , on_delete=models.CASCADE , null = True , blank = True)
    item_image = models.ImageField(upload_to='item_image/', null=True, blank=True)
    pet_type = models.CharField(max_length = 100 , null = True , blank = True)
    available_status = models.BooleanField(default = False)
    item_description = models.TextField(blank = True , null = True)
    

class StoreProduct(models.Model):  # Store's actual products
    fk_vendor = models.ForeignKey(User_Details, on_delete=models.CASCADE, null=True, blank=True)
    fk_category = models.ForeignKey(ItemCategoryMaster , on_delete=models.CASCADE , null = True , blank = True)
    item_name = models.CharField(max_length = 200 , blank = True , null = True)
    item_price = models.FloatField(blank = True , null = True, default=0)
    item_image = models.ImageField(upload_to='item_image/', null=True, blank=True)
    pet_type = models.CharField(max_length = 100 , null = True , blank = True)
    available_status = models.BooleanField(default = False)
    item_description = models.TextField(blank = True , null = True)


    