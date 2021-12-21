from rest_framework import serializers
from django.contrib.auth.models import User
from backend.models import *
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

class countrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id','Country_Name']

class BillingAddressSerializer(serializers.ModelSerializer):
    country = countrySerializer()
    class Meta:
        model = BillingAddress
        fields = ['id', 'first_name','middle_name','last_name','company','email',
        'country_code','country','phone','city','state','postal_code','address','created_date','modified_date']

class ShippigAddressSerializer(serializers.ModelSerializer):
    country = countrySerializer()
    class Meta:
        model = ShippigAddress
        fields = ['id', 'first_name','middle_name','last_name','company','email',
        'country_code','country','phone','city','state','postal_code','address','created_date','modified_date']



class CategoriesSerializer(serializers.ModelSerializer):
    banner_url = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = Categories
        fields = ['id', 'Category_Name','slug','banner_url']
    def get_image_url(self, obj):
        request = self.context.get("request")
        base_url = request.build_absolute_uri('/').strip("/")
        path = None
        if obj.banner:
            path = base_url+obj.banner.url
        return path

class ServicesCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'Category_Name','slug','Type']

class CategoriesDetailSerializer(serializers.ModelSerializer):
    banner_url = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = Categories
        fields = ['id', 'Category_Name','preview','description','slug','banner_url',
        'priority_order','created_date','modified_date']
    def get_image_url(self, obj):
        request = self.context.get("request")
        base_url = request.build_absolute_uri('/').strip("/")
        path = None
        if obj.banner:
            path = base_url+obj.banner.url
        return path


#   AttributeBase

# Attribute

class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute = serializers.SerializerMethodField('get_attribute')
    value = serializers.SerializerMethodField('get_attribute_value')
    attribute_image = serializers.SerializerMethodField('get_attribute_image')
    class Meta:
        model = ProductAttribute
        fields = ['id','attribute','value','price','attribute_image']
    
    def get_attribute(self,obj):
        return obj.attribute_ptr.base.label
    
    def get_attribute_value(self,obj):
        return obj.attribute_ptr.value

    def get_attribute_image(self,obj):
        request = self.context.get("request")
        base_url = request.build_absolute_uri('/').strip("/")
        path = ''
        if obj.attribute_ptr.Image:
            path = base_url+obj.attribute_ptr.Image.url
        return path

class ProductGallerySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = ProductGallery
        fields = ['priority_order', 'image']

    def get_image_url(self, obj):
        request = self.context.get("request")
        base_url = request.build_absolute_uri('/').strip("/")
        path = None
        if obj.Product_gallery:
            path = base_url+obj.Product_gallery.url
        return path

class ProductSerializer(serializers.ModelSerializer):
    Category = CategoriesSerializer()
    attributes = ProductAttributeSerializer(many=True)
    Product_Preview_image = serializers.SerializerMethodField('get_image_url')
    Product_Gallery = ProductGallerySerializer(many=True)
    class Meta:
        model = Product
        fields = ['id', 'Category','Product_Name','Product_Price','Product_Shipping','Product_Preview_image',
        'Product_Description','attributes','quantity','Product_Gallery']

    def get_image_url(self, obj):
        request = self.context.get("request")
        base_url = request.build_absolute_uri('/').strip("/")
        path = None
        if obj.Product_Preview_image:
            path = base_url+obj.Product_Preview_image.url
        return path
class ProductDetailSerializer(serializers.ModelSerializer):
    Category = CategoriesDetailSerializer()
    attributes = ProductAttributeSerializer(many=True)
    Product_Preview_image = serializers.SerializerMethodField('get_image_url')
    Product_Gallery = ProductGallerySerializer(many=True)
    class Meta:
        model = Product
        fields = ['id', 'Category','Product_Name','Product_Brand','Product_Color','Product_Size','Product_Connectivity','Product_Tag','Product_Article_Number','Product_Price','Product_Shipping','Product_Preview_image',
        'Product_Description','Product_TextDescription','slug','Status','priority_order','created_date','modified_date','quantity','attributes','Product_Gallery']

    def get_image_url(self, obj):
        request = self.context.get("request")
        base_url = request.build_absolute_uri('/').strip("/")
        path = None
        if obj.Product_Preview_image:
            path = base_url+obj.Product_Preview_image.url
        return path

class CartItemsSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    # attributes = serializers.SerializerMethodField('get_attribute')
    
    class Meta:
        model = CartItem
        fields = ['id','quantity','price_ht','product']
    # def get_attribute(self,obj):
    #     request = self.context.get("request")
    #     attri = ProductAttribute.objects.get(id=obj.product_variant_id)
    #     serialize = ProductAttributeSerializer(attri,context={'request':request})
    #     return serialize.data

class CartSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField('get_cart_items')
    cart_count = serializers.SerializerMethodField('get_cart_count')
    class Meta:
        model = Cart
        fields = ['status','cart_items','cart_count']
    def get_cart_items(self,obj):
        request = self.context.get("request")
        items = CartItem.objects.filter(cart=obj)
        items_serialize = CartItemsSerializer(items,many=True,context={'request':request})
        return items_serialize.data
    def get_cart_count(self,obj):
        return CartItem.objects.filter(cart=obj).count()

class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = WishlistItem
        fields = ['id','product']

class WishlistSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField('get_items')
    class Meta:
        model = Wishlist
        fields = ['items']
    def get_items(self,obj):
        request = self.context.get("request")
        wishlists = WishlistItem.objects.filter(Wishlist=obj)
        serializer = WishlistItemSerializer(wishlists,many=True,context={'request':request})
        return serializer.data

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    # product_variant = ProductAttributeSerializer()
    class Meta:
        model = OrderItem
        fields = ['quantity','Price_Paid','Shipping_Price_Paid','product','modified_date']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id','order_items','modified_date']

class UserSerializer(serializers.ModelSerializer):
    billing_address = BillingAddressSerializer()
    shipping_address = ShippigAddressSerializer()
    cart_list = serializers.SerializerMethodField('get_cart')
    wish_list = serializers.SerializerMethodField('get_wish_list')
    
    class Meta:
        model = User
        fields = ['id', 'first_name','last_name','email','billing_address','shipping_address','cart_list','wish_list']
    
    def get_cart(self,obj):
        request = self.context.get("request")
        cart = Cart.objects.filter(user=obj,status="Active").last()
        if cart is None:
            return ""
        cart_serialize = CartSerializer(cart,context={'request':request})
        return cart_serialize.data

    def get_wish_list(self,obj):
        request = self.context.get("request")
        wish = Wishlist.objects.filter(user=obj,status='active').last()
        serializer = WishlistSerializer(wish,context={'request':request})
        return serializer.data

class PageSerializer(serializers.ModelSerializer):
    Banner_Image_url = serializers.SerializerMethodField('get_bannel_url')
    Page_Feautured_Image_url = serializers.SerializerMethodField('get_Page_Feautured_Image_url')
    class Meta:
        model = Pages
        fields = ['id', 'Page_Name','Page_heading','Banner_Image_url','Page_Description','Page_Feautured_Image_url','slug','Status','Page_Role']
    
    def get_bannel_url(self, obj):
        request = self.context.get("request")
        base_url = request.build_absolute_uri('/').strip("/")
        path = None
        if obj.Banner_Image:
            path = base_url+obj.Banner_Image.url
        return path

    def get_Page_Feautured_Image_url(self, obj):
        request = self.context.get("request")
        base_url = request.build_absolute_uri('/').strip("/")
        path = None
        if obj.Banner_Image:
            path = base_url+obj.Page_Feautured_Image.url
        return path 
