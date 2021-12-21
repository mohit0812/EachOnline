from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db import IntegrityError
import json
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group
from .serializers import *
from .helpers import *
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from backend.tokens import account_activation_token
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
import stripe
from django.db.models import Avg,Count,Sum,Case, Value, When
from collections import defaultdict
stripe.api_key = "sk_test_..."

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    if email is None or password is None:
        return Response({'code': 0,'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    # try:
    user = User.objects.filter(email=email).first()
    if user is not None and user.check_password(password):
        token, _ = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user,context = {'request':request})
        return Response({'code': 1,'token': token.key,'user':serializer.data},
                    status=HTTP_200_OK)
    else:
        return Response({'code': 0,'error': 'Invalid Credentials'},
                        status=HTTP_400_BAD_REQUEST)
    # except Exception as e:
    #     return Response({'code': 0,'error': str(e)},
    #             status=HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def signup(request):
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    name = data.get('first_name')
    role = data.get('userType')
    if email is None:
        return Response({'code': 0,'message': 'Please provide email'},
                    status=HTTP_404_NOT_FOUND)
    if password is None:
        return Response({'code': 0,'message': 'Please provide password'},
                    status=HTTP_404_NOT_FOUND)
    if role is None:
        return Response({'code': 0,'message': 'Please provide role'},
                    status=HTTP_404_NOT_FOUND)
    try:
        user = User(first_name=name,email=email,username=email)
        user.set_password(password)
        user.is_active = False
        user.save()
        group = Group.objects.get(name=role) 
        group.user_set.add(user)
        current_site = get_current_site(request)
            
        to_email = email
        subject, from_email, to = 'Activation of your account at Each Online', 'test@gmail.com' , to_email
        text_content = 'Activation of your account at Each Online.'
        html_content = render_to_string('email/client_acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
            'password':password,
        })
        
    
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as e:
        return Response({'code': 0,'message': str(e)},
                    status=HTTP_404_NOT_FOUND)
    return Response({'code': 1,"message":"Activation link sent on email."},
            status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def change_password(request):
    data = json.loads(request.body)
    password = data.get('password')
    new_password = data.get('new_password')
    try:
        user = User.objects.get(id=request.user.id)
        if user.check_password(password):
            user.set_password(new_password)
            user.save()
        else:
            return Response({'code': 0,'error': 'Old password does not match.'},
                        status=HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'code': 0,'error': str(e)},
                        status=HTTP_400_BAD_REQUEST)
    return Response({'code': 1,'message': 'Password changed successfully'},
                status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def update_profile(request):
    data = json.loads(request.body)
    first_name = data.get('first_name',None)
    last_name = data.get('last_name',None)
    email = data.get('email',None)
    try:
        user = User.objects.get(id=request.user.id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
    except Exception as e:
        return Response({'code': 0,'error': str(e)},
                        status=HTTP_400_BAD_REQUEST)
    return Response({'code': 1,'message': 'Profile updated successfully'},
                status=HTTP_200_OK)

@csrf_exempt
@api_view(["GET"])
def get_currentuser(request):
    try:
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user,context = {'request':request})
    except Exception as e:
        return Response({'code': 0,'error': str(e)},
                        status=HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'code': 1,'token': token.key,'user':serializer.data},
                status=HTTP_200_OK)

@csrf_exempt
@api_view(["GET","POST"])
def user_billing_address(request):
    user = request.user
    if request.method == "GET":
        try:
            serializer = BillingAddressSerializer(user.billing_address)
        except Exception as e:
            return Response({'code': 0,'error': str(e)},
                            status=HTTP_400_BAD_REQUEST)
        return Response({'code': 1,'data':serializer.data},
                    status=HTTP_200_OK)
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            country = Country.objects.get(Country_Name=data.get('country'))
            try:
                address = user.billing_address
                data['country'] = country
                for key, value in data.items():
                    setattr(address, key, value)
                address.save()   
            except ObjectDoesNotExist:
                data['country'] = country
                address = BillingAddress(**data)
                address.user = user
                address.save()
            serializer = BillingAddressSerializer(user.billing_address)
        except Exception as e:
            print(e)
            return Response({'code': 0,'error': str(e)},
                            status=HTTP_400_BAD_REQUEST)
        return Response({'code': 1,'billing_address':serializer.data},
                    status=HTTP_200_OK)

@csrf_exempt
@api_view(["GET","POST"])
def user_shipping_address(request):
    user = request.user
    if request.method == "GET":
        try:
            serializer = ShippigAddressSerializer(user.billing_address)
        except Exception as e:
            return Response({'code': 0,'error': str(e)},
                            status=HTTP_400_BAD_REQUEST)
        return Response({'code': 1,'data':serializer.data},
                    status=HTTP_200_OK)
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            country = Country.objects.get(Country_Name=data.get('country'))
            try:
                address = user.shipping_address
                data['country'] = country
                for key, value in data.items():

                    setattr(address, key, value)
                address.save()   
            except ObjectDoesNotExist:
                data['country'] = country
                address = ShippigAddress(**data)
                address.user = user
                address.save()
            serializer = ShippigAddressSerializer(user.billing_address)
        except Exception as e:
            print(e)
            return Response({'code': 0,'error': str(e)},
                            status=HTTP_400_BAD_REQUEST)
        return Response({'code': 1,'shipping_address':serializer.data},
                    status=HTTP_200_OK)

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def get_products(request):
    current_page = int(request.GET.get('page' ,'1'))
    limit = 20 * int(current_page)
    offset = limit - 20
    query = None
    category = request.GET.get('category',None)
    categoryList = request.GET.getlist('categoryId',None)
    price = request.GET.get('price',None)
    if category is not None:
        category_obj = Categories.objects.get(slug=category)
        if category_obj is not None:
            query = Q(Category=category_obj)
    if len(categoryList) != 0:
        for catId in categoryList:
            cate_obj = Categories.objects.get(id=catId)
            if cate_obj is not None:
                if query is not None:
                    query = query | Q(Category=cate_obj)
                else:
                    query = Q(Category=cate_obj)
    if price is not None:
        price = price.split("-")
        if query is not None:
            if len(price) > 1:
                query = query & Q(Product_Price__gte=price[0]) & Q(Product_Price__lte=price[1])
            else:
                query = query & Q(Product_Price__gte=price[0]) 
        else:
            if len(price) > 1:
                query = Q(Product_Price__gte=price[0]) & Q(Product_Price__lte=price[1])
            else:
                query = Q(Product_Price__gte=price[0]) 
    try:
        if query is not None:
            query = query & Q(Category__Type='Product') 
            products = Product.objects.filter(query)[offset:limit]
            allProducts = Product.objects.filter(query)
        else:
            products = Product.objects.filter(Category__Type='Product')[offset:limit]
            allProducts = Product.objects.filter(Category__Type='Product')
        serializer = ProductSerializer(products, many=True,context = {'request':request})
        pagination = create_pagination(len(allProducts),current_page)
    except ObjectDoesNotExist:
        return Response({'code': 0,'error': 'product does not exist.'},
                        status=HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'code': 0,'error': str(e)},
                        status=HTTP_400_BAD_REQUEST)
    return Response({'code': 1,'data': {'products':serializer.data,'pagination':pagination}},
                status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def SearchProduct(request):
    keyword = request.GET.get('keyword',None)
    try:
        products = Product.objects.filter(Q(Product_Name__icontains=keyword) | Q(slug__icontains=keyword) | 
        Q(Product_Brand__icontains=keyword) | Q(Category__Category_Name__icontains=keyword) | 
        Q(Category__slug__icontains=keyword))[:5]
        serializer = ProductSerializer(products, many=True,context = {'request':request})
    except ObjectDoesNotExist:
        return Response({'code': 0,'error': 'product does not exist.'},
                        status=HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'code': 0,'error': str(e)},
                        status=HTTP_400_BAD_REQUEST)
    return Response({'code': 1,'data': {'products':serializer.data}},
                status=HTTP_200_OK)

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def get_product(request,productId):

    try:
        product = Product.objects.get(id=productId)
        related_products = Product.objects.filter(Category_id=product.Category_id)[:20]
        serializer = ProductDetailSerializer(product,context = {'request':request})
        related_serializer = ProductSerializer(related_products,many=True,context = {'request':request})
    except ObjectDoesNotExist:
        return Response({'code': 0,'error': 'product does not exist.'},
                        status=HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'code': 0,'error': str(e)},
                        status=HTTP_400_BAD_REQUEST)
    return Response({'code': 1,'data':{'product':serializer.data,'related_products': related_serializer.data}},
                status=HTTP_200_OK)

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def get_categories(request):
    try:
        categories = Categories.objects.filter(Type='Product')
        service_categories = Categories.objects.filter(Type='Service')
        serializer = CategoriesSerializer(categories, many=True,context = {'request':request})
        service_serializer = CategoriesSerializer(service_categories, many=True,context = {'request':request})
    except ObjectDoesNotExist:
        return Response({'code': 0,'error': 'Categories does not exist.'},
                        status=HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'code': 0,'error': str(e)},
                        status=HTTP_400_BAD_REQUEST)
    return Response({'code': 1,'data': serializer.data,'service_categories': service_serializer.data},
                status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def CreateCart(request):
    data = json.loads(request.body)
    ProductId = data.get('ProductId',None)
    # AttributeId = data.get('AttributeId',None)
    quantity = data.get('quantity',None)
    if ProductId is not None and quantity is not None and quantity > 0:
        ProductInstance = get_object_or_404(Product, pk=ProductId)
        price=ProductInstance.Product_Price
        ProductInstance.quantity = ProductInstance.quantity - int(quantity)
        ProductInstance.save()
        try:
            CurrentCart=Cart.objects.get(user_id=request.user.id)
            serializer = CartSerializer(CurrentCart,context={'request':request})
            IsProductInCart = CartItem.objects.filter(cart_id=CurrentCart.pk,product=ProductInstance).last()
            if IsProductInCart:
                IsProductInCart.quantity = int(IsProductInCart.quantity) + quantity
                IsProductInCart.save()
                # cartcount=CartItem.objects.filter(cart_id=CurrentCart.pk).count()
                return Response({'code': 1,'status':'repeated','cart_list':serializer.data},
                        status=HTTP_200_OK)
            else:
                CartItem.objects.create(product=ProductInstance,price_ht=price,cart=CurrentCart,quantity=quantity)
                cartcount=CartItem.objects.filter(cart_id=CurrentCart.pk).count()
                return Response({'code': 1,'status':'new','cart_list':serializer.data},
                        status=HTTP_200_OK)
        except Cart.DoesNotExist:
            CurrentCart = None
            cartint=Cart.objects.create(user=request.user)
            CartItem.objects.create(product=ProductInstance,price_ht=price,cart=cartint,quantity=quantity)
            serializer = CartSerializer(cartint,context={'request':request})
            return Response({'code': 1,'status':'new','cart_list':serializer.data},
                        status=HTTP_200_OK)
    
    return Response({'code': 0,'cartcount':request.POST.get('ProductId')},
            status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def removeFromCart(request):
    data = json.loads(request.body)
    ProductId = data.get('ProductId',None)
    removeAll = data.get('removeAll',None)
    quantity = data.get('quantity',False)
    if ProductId:
        ProductInstance = get_object_or_404(Product, pk=ProductId)
        price=ProductInstance.Product_Price
        try:
            CurrentCart=Cart.objects.get(user_id=request.user.id)
            serializer = CartSerializer(CurrentCart,context={'request':request})
            IsProductInCart = CartItem.objects.filter(cart_id=CurrentCart.pk,product=ProductInstance).last()
            if IsProductInCart:
                if quantity:
                    if int(IsProductInCart.quantity) > 1:
                        IsProductInCart.quantity = int(IsProductInCart.quantity)-1
                        IsProductInCart.save()
                else:
                    IsProductInCart.delete()
                # cartcount=CartItem.objects.filter(cart_id=CurrentCart.pk).count()
                return Response({'code': 1,'messsage':'Item removed','cart_list':serializer.data},
                        status=HTTP_200_OK)
            else:
                return Response({'code': 0,'messsage':'Item does not exist'},
                        status=HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'code': 0,'messsage':'Item does not exist'},
                        status=HTTP_200_OK)
    else:
        if removeAll:
            CurrentCart=Cart.objects.get(user_id=request.user.id)
            serializer = CartSerializer(CurrentCart,context={'request':request})
            CartItem.objects.filter(cart_id=CurrentCart.pk).delete()
            return Response({'code': 1,'message':'cart empty','cart_list':serializer.data},
                        status=HTTP_200_OK)
    return Response({'code': 0,'cartcount':request.POST.get('ProductId')},
            status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def getPages(request,role):
    try:
        page = Pages.objects.get(Status='Publish',Page_Role=role)
        serializer = PageSerializer(page,context = {'request':request})
        return Response({'code': 1,'page':serializer.data},
            status=HTTP_200_OK)
    except Pages.DoesNotExist:
        return Response({'code': 0,'message':'Page is not exist.'},
            status=HTTP_200_OK)
    except Exception as e:
        return Response({'code': 0,'message': str(e)},
            status=HTTP_400_BAD_REQUEST)
    return Response({'code': 0,'message': 'Plese try again.'},
            status=HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["POST"])
def CreateWishList(request):
    data = json.loads(request.body)
    ProductId = data.get('ProductId',None)
    all = data.get('all',None)
    if all is not None:
        try:
            CurrentWishlist=Wishlist.objects.get(user_id=request.user.id, status='Active')
            serializer = WishlistSerializer(CurrentWishlist,context={'request':request})
            WishlistItem.objects.filter(Wishlist=CurrentWishlist).delete()
            return Response({'code': 1,'status':'remove','message':'All products removed from wishlist.','wish_list':serializer.data},
                        status=HTTP_200_OK)
        except Wishlist.DoesNotExist:
            return Response({'code': 1,'status':'remove','message':'All products removed from wishlist.','wish_list':serializer.data},
                status=HTTP_200_OK)
    if ProductId is not None:
        ProductInstance = get_object_or_404(Product, pk=ProductId)
        try:
            CurrentWishlist=Wishlist.objects.get(user_id=request.user.id, status='Active')
            serializer = WishlistSerializer(CurrentWishlist,context={'request':request})
            IsProductInWishlist = WishlistItem.objects.filter(product=ProductInstance,Wishlist=CurrentWishlist).last()
            if IsProductInWishlist:
                IsProductInWishlist.delete()
                return Response({'code': 1,'status':'remove','message':'Project removed from wishlist.','wish_list':serializer.data},
                        status=HTTP_200_OK)
            else:
                WishlistItem.objects.create(product=ProductInstance,Wishlist=CurrentWishlist)
                return Response({'code': 1,'status':'add','message':'Project added in wishlist.','wish_list':serializer.data},
                        status=HTTP_200_OK)
        except Wishlist.DoesNotExist:
            CurrentWishlist = None
            cartint=Wishlist.objects.create(user=request.user, status='Active')
            WishlistItem.objects.create(product=ProductInstance,Wishlist=cartint)
            serializer = WishlistSerializer(cartint,context={'request':request})
            return Response({'code': 1,'status':'add','message':'Project added in wishlist.','wish_list':serializer.data},
                        status=HTTP_200_OK)
    
    return Response({'code': 0,'message':'Product is invalid.'},
            status=HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(["POST"])
def CheckOut(request):
    stripe.api_key = 'sk_test_51HTt4sJOxKwQ6C0za7HJmwXzzPbGQah2NpyQsVdLCmk1dQgfrjGZ9u7ec5CqDeTBX70j3Ghu7x6fF6M5S6tloClU00p11VH5k0'
    try:
        currentcart=Cart.objects.get(user_id=request.user.id).pk
        totalprice=CartItem.objects.filter(cart_id=currentcart).aggregate(Sum('price_ht'))
        CartProducts=CartItem.objects.filter(cart_id=currentcart)
        currentuser=''
        price=0
        for cartdata in CartProducts:
            if cartdata.product_variant:
                productattrprice=ProductAttribute.objects.get(attribute_ptr_id=cartdata.product_variant)
                price+= productattrprice.price if productattrprice.price else 0 
                price+= productattrprice.Shipping if productattrprice.Shipping else 0
            else:
                price+= cartdata.product.Product_Price * cartdata.quantity if cartdata.product.Product_Price else 0 
                price+= cartdata.product.Product_Shipping if cartdata.product.Product_Shipping else 0
        customer = stripe.Customer.create(
            name = request.user.first_name,
            email=request.user.email,
            address={
                "line1":'us',
                "city": 'us',
                "state": 'us',
                "country": 'US',
                "postal_code": '14301',
            },
        
        ) 
        payment_intent = stripe.PaymentIntent.create(
            amount=int(price)*100,
            currency='usd',
            customer=customer.id,
            payment_method_types=['card'],
            description="Eachonline Cart Checkout"
        )
        
        OrderCreated=Order(CustomerId=customer.id,cart_id=currentcart,user_id=request.user.id,CustomerIdPaymentGateway='Stripe',chargeId=payment_intent.id,currency=payment_intent.currency,Status=0)
        OrderCreated.save()

        return Response({'code': 1,'client_secret':payment_intent.client_secret,'orderid':OrderCreated.pk},
            status=HTTP_200_OK)
    except Exception as e:
        return Response({'code': 0,'message':str(e)},
            status=HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(["POST"])
def paymentStripeDone(request):
    data = json.loads(request.body)
    orderid = data.get("orderid",None)
    stripe.api_key = 'sk_test_51HTt4sJOxKwQ6C0za7HJmwXzzPbGQah2NpyQsVdLCmk1dQgfrjGZ9u7ec5CqDeTBX70j3Ghu7x6fF6M5S6tloClU00p11VH5k0'
    try:
        # add products from cart to order item
        GetOrder=Order.objects.get(id=orderid)
        currentcart=Cart.objects.get(user_id=request.user.id).pk
        CartProducts=CartItem.objects.filter(cart_id=currentcart)
        GetOrder.Status=1
        GetOrder.save()

        Rate=Credits.objects.all()
        Manager_Rate=''
        Con_Manager=''
        Sme_Rate=''
        for rate in Rate:
            Manager_Rate=rate.Manager_Rate
            Con_Manager=rate.Manufacturer_Rate
            Sme_Rate=rate.Sme_Rate

        for prd in CartProducts:
            print(prd)
            shippingprice=0
            total_price_single_prd=0
            if prd.product_variant:
                productattrprice=ProductAttribute.objects.get(attribute_ptr_id=prd.product_variant)
                shippingprice= productattrprice.Shipping if productattrprice.Shipping else 0
            else:
                shippingprice=prd.product.Product_Shipping if prd.product.Product_Shipping else 0
            
            total_price_single_prd=prd.product.Product_Price * prd.quantity
            total_price_single_prd+=shippingprice
            
            GetSmeSingleAmount=total_price_single_prd*Sme_Rate/100
            GetManagerSingleAmount=total_price_single_prd*Manager_Rate/100
            GetConManagerSingleAmount=total_price_single_prd*Con_Manager/100
            
            # For Single OrderItem Payout to each user
            
            Sme_Id=ParentUser.objects.get(current_user=prd.product.Owner)
            
            Conceirge_User=ParentUser.objects.get(current_user_id=Sme_Id.parent_user_id)
            Conceirge_Id=Conceirge_User.id


            Manager_User=ParentUser.objects.get(current_user_id=Conceirge_User.parent_user_id)
            Manager_Id=Manager_User.id
            
            PayoutCreatedSme=Payout(user=Sme_Id.current_user,order=GetOrder,sme_amount=GetSmeSingleAmount)
            PayoutCreatedSme.save()

            PayoutCreatedconceirge=Payout(user=Conceirge_User.current_user,order=GetOrder,conceirge_amount=GetConManagerSingleAmount)
            PayoutCreatedconceirge.save()

            PayoutCreated=Payout(user=Manager_User.current_user,order=GetOrder,manager_amount=GetManagerSingleAmount)
            
            PayoutCreated.save()
            # For Payout End
            
            # Create Orderitem table
            OrderItemCreated=OrderItem(product=prd.product,Price_Paid=prd.product.Product_Price * prd.quantity,quantity=prd.quantity,Shipping_Price_Paid=shippingprice,product_variant=prd.product_variant if prd.product_variant else None ,order=GetOrder,sme_amount=GetSmeSingleAmount,manager_amount=GetManagerSingleAmount,conceirge_amount=GetConManagerSingleAmount)
            OrderItemCreated.save()
            
       
        # Transfer Money to Each Role Using Stripe Connect
        data = defaultdict(list)
        currentuser=''
        price=0
        for cartdata in CartProducts:
            if cartdata.product.Owner.id == currentuser:
                price+=cartdata.product.Product_Price * cartdata.quantity if cartdata.product.Product_Price else 0
                
                price+=cartdata.product.Product_Shipping if cartdata.product.Product_Shipping else 0
                
                data[cartdata.product.Owner.id]=price
            else:
                currentuser=''
                currentuser=cartdata.product.Owner.id
                
                if cartdata.product_variant:
                    productattrprice=ProductAttribute.objects.get(attribute_ptr_id=cartdata.product_variant)
                    
                    price+= productattrprice.price * productattrprice.variant_quantity if productattrprice.price else 0 

                    price+= productattrprice.Shipping if productattrprice.Shipping else 0
                else:
                    price+= cartdata.product.Product_Price * cartdata.quantity if cartdata.product.Product_Price else 0 

                    price+=cartdata.product.Product_Shipping if cartdata.product.Product_Shipping else 0
                    
            stripeaccount=''
            data[cartdata.product.Owner.id]=price
        
        alldata=dict(data)
        for k in alldata:
            total_price=alldata[k]
            
            GetSmeAmount=int(total_price)*Sme_Rate/100
            GetManagerAmount=int(total_price)*Manager_Rate/100
            GetConManagerAmount=int(total_price)*Con_Manager/100
            
            
            Sme_Stripe=ParentUser.objects.get(current_user_id=k)
            Sme_Stripe_Connect=Sme_Stripe.stripe_connect
            
            Conceirge_Stripe=ParentUser.objects.get(current_user_id=Sme_Stripe.parent_user_id)
            Conceirge_Stripe_Connect=Conceirge_Stripe.stripe_connect


            Manager_Stripe=ParentUser.objects.get(current_user_id=Conceirge_Stripe.parent_user_id)
            Manager_Stripe_Connect=Manager_Stripe.stripe_connect
            
            transfer = stripe.Transfer.create(
                amount=int(GetSmeAmount)*100,
                currency='usd',
                destination=Sme_Stripe_Connect,
                transfer_group='{ORDER10}',
            )

            transfer = stripe.Transfer.create(
                amount=int(GetManagerAmount)*100,
                currency='usd',
                destination=Manager_Stripe_Connect,
                transfer_group='{ORDER10}',
            )

            transfer = stripe.Transfer.create(
                amount=int(GetConManagerAmount)*100,
                currency='usd',
                destination=Conceirge_Stripe_Connect,
                transfer_group='{ORDER10}',
            )
            # return Response({'code': 1,'message':"Payment Completed."},
            #     status=HTTP_200_OK)
        CartProducts.delete()
        return Response({'code': 1,'message':str(currentcart)},
                status=HTTP_200_OK)
    except Exception as e:
        
        return Response({'code': 0,'message':str(e)},
            status=HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def ordersList(request):
    try:
        orders = Order.objects.filter(user=request.user,Status=1)
        serializer = OrderSerializer(orders,many=True,context={'request':request})
        return Response({'code': 1,"orders":serializer.data},
                status=HTTP_200_OK)
    except Exception as e:
        return Response({'code': 0,'message':str(e)},
            status=HTTP_400_BAD_REQUEST)



    return Response({'code': 1,'message':"Payment Completed."},
        status=HTTP_200_OK)
