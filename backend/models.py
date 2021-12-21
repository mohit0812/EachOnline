from django.db import models
from autoslug.fields import AutoSlugField
from django.contrib.auth.models import User,Group
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.core.files.storage import FileSystemStorage
from datetime import date
import os
# Create your models here.
class Country(models.Model):
    Country_Name=models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    
    def __str__(self):
        return self.Country
    class Meta:
       ordering = ('-created_date',)
    
class Manufacturer(models.Model):
    Manufacturer_Name=models.CharField(max_length=100)
    Manufacturer_Address = models.TextField(blank=True,null=True)
    Manufacturer_Country=models.ForeignKey(Country, on_delete=models.CASCADE,blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    
    def __str__(self):
        return self.Country
    
    class Meta:
       ordering = ('-created_date',)

class Categories(models.Model):
    CategoryType = (
        ('Product', 'Product'),
        ('Service', 'Service'),
    )
    Type=models.CharField(max_length=20, choices=CategoryType,default='Product')
    Category_Name=models.CharField(max_length=100)
    preview= models.ImageField(upload_to='Category-Preview',blank=True,null=True)
    description=RichTextUploadingField(blank=True,null=True)
    slug = AutoSlugField(populate_from='Category_Name',always_update=True,unique=True,blank=True,null=True, db_index=True)
    banner= models.ImageField(upload_to='Category-Banner',blank=True,null=True)
    priority_order=models.IntegerField(blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    def __str__(self):
        return self.Category_Name
    class Meta:
       ordering = ('priority_order',)


class Product(models.Model):
    Category=models.ForeignKey(Categories, on_delete=models.CASCADE)
    Owner=models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    Product_Name=models.TextField(blank=True,null=True)
    Product_Brand=models.TextField(blank=True,null=True)
    Product_Color=models.TextField(blank=True,null=True)
    Product_Size=models.TextField(blank=True,null=True)
    Product_Connectivity=models.TextField(blank=True,null=True)
    Product_Tag=models.TextField(blank=True,null=True)
    quantity=models.IntegerField(blank=True,null=True)
    Product_Article_Number=models.CharField(max_length=100,null=True,blank=True,unique=True)
    Product_Price=models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    Product_Shipping=models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    Product_Preview_image=models.ImageField(upload_to='Product_image',blank=True,null=True,default='')
    Product_Description=RichTextUploadingField(blank=True,null=True)
    Product_TextDescription=models.TextField(blank=True,null=True)
    slug = AutoSlugField(populate_from='Product_Name',always_update=True,unique=True,blank=True,null=True, db_index=True)
    Status=models.BooleanField(default=True)
    priority_order=models.IntegerField(blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    def __str__(self):
        return self.Product_Name
    def add_all_attributes(self):
        for attribute in Attribute.objects.all():
            self.attributes.add(attribute)
    def add_all_attributes_for_base(self, label):
        base = AttributeBase.objects.get(label=label)
        for attribute in base.attributes.all():
            self.attributes.add(attribute)
    class Meta:
       ordering = ('priority_order',)


class ProductGallery(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE,related_name='Product_Gallery')
    Product_gallery=models.FileField(upload_to='Product_Gallery',blank=True,null=True)
    priority_order=models.IntegerField(blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    def __str__(self):
        name , extension = os.path.split(self.Product_gallery.name)
        
        return extension

    class Meta:
       ordering = ('priority_order',)

class AttributeBase(models.Model):
    label = models.CharField(max_length=255) # e.g. color, size, shape, etc.
    def __str__(self):
        return self.label

class Attribute(models.Model):
    base = models.ForeignKey('AttributeBase', related_name='attributes', on_delete=models.CASCADE)
    value = models.CharField(max_length=255) # e.g. red, L, round, etc.
    internal_value = models.CharField(max_length=255, null=True, blank=True) 
    Image=models.ImageField(upload_to='Product_Variant',blank=True,null=True)
    def __str__(self):
        return self.value
    
class ProductAttribute(Attribute):
    product = models.ForeignKey('Product', related_name='attributes', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    Shipping=models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    variant_quantity=models.IntegerField(blank=True,null=True)

class ParentUser(models.Model):
    current_user=models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True, related_name='currents')
    parent_user=models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True, related_name='parents')
    stripe_connect=models.CharField(max_length=255,blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    def __str__(self):
        return self.parent_user.username


class Pages(models.Model):
    
    PAGECHOICES = (
        ('Publish', 'Publish'),
        ('Draft', 'Draft'),
        
    )
    PageRole = (
        ('Content', 'Content'),
        ('About', 'About'),
        ('Contact', 'Contact'),
        ('Privacy', 'Privacy'),
        ('Partner', 'Partner'),
        ('Term', 'Term of use'),
        ('Return', 'Return Policy'),
    )
    
    Page_Name=models.CharField(max_length=100)
    Page_heading=models.CharField(max_length=100,blank=True,null=True)
    Banner_Image=models.ImageField(upload_to='Page_Banner_Images',blank=True,null=True)
    Page_Description=RichTextUploadingField()
    Page_Feautured_Image=models.ImageField(upload_to='Page_Feautured_Images',blank=True,null=True)
    slug = AutoSlugField(populate_from='Page_Name',always_update=True,unique=True,blank=True,null=True)
    Status=models.CharField(max_length=20, choices=PAGECHOICES,default='Publish')
    Page_Role=models.CharField(max_length=20, choices=PageRole,default=0)
    created_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    def __str__(self):
        return self.Page_Name

    class Meta:
       ordering = ('-created_date',)

class Credits(models.Model):
    Manager_Rate=models.IntegerField(help_text='Insert pointt convertsion rate to money (Only INT Like : 10 )')
    Manufacturer_Rate=models.IntegerField(help_text='Insert start limits for converting points to money (Only INT Like : 100 )')
    Sme_Rate=models.IntegerField(help_text='Insert last limits for converting points to money (Only INT Like : 100 )')
    created_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    
    def __str__(self):
        return str(self.Manager_Rate)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status=models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(Attribute, on_delete=models.CASCADE,blank=True,null=True)
    quantity = models.IntegerField(default=1)
    price_ht = models.FloatField(blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    TAX_AMOUNT = 19.25
    
    def price_ttc(self):
        return self.price_ht * (1 + TAX_AMOUNT/100.0)




class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status=models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    

class WishlistItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    Wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    TAX_AMOUNT = 19.25
    def price_ttc(self):
        return self.price_ht * (1 + TAX_AMOUNT/100.0)





class Order(models.Model):
    PageRole = (
        ('New', 'New'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT)
    CustomerId = models.TextField(blank=True,null=True)
    CustomerIdPaymentGateway=models.TextField(blank=True,null=True)
    chargeId=models.TextField(blank=True,null=True)
    currency=models.TextField(blank=True,null=True)
    Status=models.BooleanField(default=False)
    Type=models.CharField(max_length=20, choices=PageRole,default='New')
    created_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True,null=True)

    class Meta:
       ordering = ('-created_date',)

class Payout(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    order = models.ForeignKey(Order,on_delete=models.CASCADE,blank=True,null=True)
    sme_amount=models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    manager_amount=models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    conceirge_amount=models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    class Meta:
       ordering = ('-created_date',)

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,blank=True,null=True,related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_variant = models.ForeignKey(Attribute, on_delete=models.CASCADE,blank=True,null=True)
    quantity = models.IntegerField(default=1)
    sme_amount=models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    manager_amount=models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    conceirge_amount=models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modified_date = models.DateTimeField(auto_now=True,blank=True,null=True)
    Price_Paid=models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    Shipping_Price_Paid=models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    class Meta:
       ordering = ('-created_date',)


class BillingAddress(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='billing_address')
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50,blank=True,null=True)
    last_name =  models.CharField(max_length=50)
    company = models.CharField(max_length=50,blank=True,null=True)
    email = models.CharField(max_length=100)
    country_code = models.IntegerField()
    country=models.ForeignKey(Country, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100,blank=True,null=True)
    postal_code = models.IntegerField()
    address = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name

class ShippigAddress(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='shipping_address')
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50,blank=True,null=True)
    last_name =  models.CharField(max_length=50)
    company = models.CharField(max_length=50,blank=True,null=True)
    email = models.CharField(max_length=100)
    country_code = models.IntegerField()
    country=models.ForeignKey(Country, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100,blank=True,null=True)
    postal_code = models.IntegerField()
    address = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name

