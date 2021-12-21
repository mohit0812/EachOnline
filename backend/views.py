from __future__ import absolute_import, unicode_literals
import stripe
import logging
import sys
import pyzipper
from django.views.generic.base import TemplateView
from django.contrib.auth.tokens import *
from .decorators import *
from .tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from backend.forms import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from datetime import datetime
from django.core.mail import EmailMessage
from django.contrib import messages
from django.urls import reverse
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.serializers import serialize
from django.core import serializers

import os
from django.dispatch import receiver
from django.core.signals import request_finished
from django.db.models.signals import post_save
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User, Group

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import json
from collections import defaultdict
from django.db.models import Avg, Count, Sum, Case, Value, When
from django.core.files.storage import FileSystemStorage
import requests
import tempfile
import urllib 
from urllib.request import urlopen
from django.core import files
from django.conf import settings
your_media_root = settings.MEDIA_ROOT
import csv #will get csv from python


stripe.api_key = "sk_test_..."
# Create your views here.


def index(request):
    if request.user.is_authenticated:
        return render(request, "adminlte/base.html")
    return render(request, "adminlte/login.html", {'form': AuthenticationForm})


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            return render(request, "adminlte/login.html", {'form': form})
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return redirect('index')


def logout_request(request, templateview):
    logout(request)
    messages.info(request, "Logged out successfully!")
    if templateview == 'frontend':
        return redirect('frontendindex')
    else:
        return redirect("index")


@group_required('Administrator', login_url='index')
def show_manufacturer(request):
    try:
        All_Manufacturer = Manufacturer.objects.all()
    except Exception as e:
       All_Manufacturer = False
    return render(request, "adminlte/manufacturer/show-manufacturers.html", {'manufacturer': All_Manufacturer})


@group_required('admin', login_url='index')
def add_manufacturer(request):
    if request.method == 'POST':
        form = ManufacturerForm(request.POST)
        if form.is_valid():
            manufacturer = form.save()
            messages.success(request, 'Manufacturer Added succesfully..')
            return redirect('ShowProject')
        else:
            return render(request, "adminlte/manufacturer/create-manufacturer.html", {'form': form})

    return render(request, "adminlte/manufacturer/create-manufacturer.html", {'form': ManufacturerForm})


@group_required('Administrator', login_url='index')
def edit_manufacturer(request, id):
    ManufacturerInstance = get_object_or_404(Manufacturer, pk=id)
    if request.method == 'POST':
        form = ManufacturerForm(request.POST, instance=ManufacturerInstance)
        if form.is_valid:
            manufacturer = form.save()
            messages.success(request, 'Manufacturer Updated succesfully..')
            return redirect('ShowManufacturer')
        else:
            return render(request, "adminlte/manufacturer/create-manufacturer.html", {'form': form, 'id': id})

    form = ManufacturerForm(instance=ManufacturerInstance)
    return render(request, "adminlte/manufacturer/create-manufacturer.html", {'form': form, 'id': id})


@group_required('admin', login_url='index')
def add_category(request):
    if request.method == 'POST':
        category_form = CategoryForm(request.POST, request.FILES)
        if category_form.is_valid():
            categoryform = category_form.save()
            messages.success(request, 'Category Added succesfully..')
            return redirect('ShowProductCategory')
        else:
            return render(request, "adminlte/product/create-category.html", {'form': category_form})
    else:
        return render(request, "adminlte/product/create-category.html", {'form': CategoryForm})


@group_required('Administrator', login_url='index')
def show_product_category(request):
    try:
        All_Categories = Categories.objects.all()
    except Exception as e:
       All_Categories = False
    return render(request, "adminlte/product/show-categories.html", {'All_Categories': All_Categories})


@group_required('Administrator', login_url='index')
def edit_product_category(request, id):
    if request.method == 'POST':
        obj = get_object_or_404(Categories, pk=id)
        if obj:
            Credits_Form = CategoryForm(
                request.POST, request.FILES, instance=obj)
            if Credits_Form.is_valid:
                Credits_Form.save()
                messages.success(request, str(
                    obj.Category_Name)+' Updated succesfully..')
                return redirect('ShowProductCategory')
            else:
                return render(request, "adminlte/product/create-category.html", {'form': Credits_Form, 'id': id})
        else:
            raise Http404("No MyModel matches the given query.")
    ProjectInstance = get_object_or_404(Categories, pk=id)
    form = CategoryForm(instance=ProjectInstance)
    return render(request, "adminlte/product/create-category.html", {'form': form, 'id': id})


@group_required('Administrator', login_url='index')
def single_product_category(request, id):
    IsCategory = Categories.objects.filter(pk=id)
    return render(request, "adminlte/product/ShowSingleCategory.html", {'cat': IsCategory})


@group_required('Administrator', login_url='index')
def delete_product_category(request, id):
    ProjectInstance = get_object_or_404(Categories, pk=id)
    if ProjectInstance:
        messages.success(request, str(
            ProjectInstance.Category_Name)+' Deleted succesfully..')
        ProjectInstance.delete()
        return redirect('ShowProductCategory')


@group_required('Administrator', login_url='index')
def add_user(request):
    return render(request, "adminlte/user/createuser.html", {'form': SignUpForm, 'detailform': UserDetailForm})


@group_required('Administrator', login_url='index')
def edit_user(request, id):
    try:
        UserDetailInstance = ParentUser.objects.get(current_user_id=id)
        detailform = UserDetailForm(instance=UserDetailInstance)
    except ParentUser.DoesNotExist:
        UserDetailInstance = ParentUser(current_user_id=id)
        detailform = UserDetailForm(instance=UserDetailInstance)

    if request.method == 'POST':
        Detail_User_Form = UserDetailForm(
            request.POST, request.FILES, instance=UserDetailInstance)
        if Detail_User_Form.is_valid:
            Detail_User_Form.save()
            messages.success(request, 'Updated succesfully..')
            return redirect('userdetail', id)
        else:
            return render(request, "adminlte/user/EditRole.html", {'form': '', 'detailform': Detail_User_Form, 'id': id,'type':'conceirge'})

    return render(request, "adminlte/user/EditRole.html", {'form': '', 'detailform': detailform, 'id': id,'type':'conceirge'})

@group_required('Administrator', login_url='index')
def edit_sme_user(request, id):
    try:
        UserDetailInstance = ParentUser.objects.get(current_user_id=id)
        detailform = SMEUserDetailForm(instance=UserDetailInstance)
    except ParentUser.DoesNotExist:
        UserDetailInstance = ParentUser(current_user_id=id)
        detailform = SMEUserDetailForm(instance=UserDetailInstance)

    if request.method == 'POST':
        Detail_User_Form = SMEUserDetailForm(
            request.POST, request.FILES, instance=UserDetailInstance)
        if Detail_User_Form.is_valid:
            Detail_User_Form.save()
            messages.success(request, 'Updated succesfully..')
            return redirect('userdetail', id)
        else:
            return render(request, "adminlte/user/EditRole.html", {'form': '', 'detailform': Detail_User_Form, 'id': id,'type':'sme'})

    return render(request, "adminlte/user/EditRole.html", {'form': '', 'detailform': detailform, 'id': id,'type':'sme'})


@group_required('Administrator', login_url='index')
def show_users(request):
    All_Users = User.objects.all()
    return render(request, "adminlte/user/showusers.html", {'All_Users': All_Users})

@group_required('Administrator', login_url='index')
def show_consumers(request,name):
    
    All_Users = User.objects.filter(groups__name=name)
    return render(request, "adminlte/user/showusers.html", {'All_Users': All_Users})


@group_required('Regional Manager', login_url='index')
def show_concierge_users(request):
    All_Users = ParentUser.objects.filter(parent_user_id=request.user.id)
    return render(request, "adminlte/user/showconceirgeusers.html", {'All_Users': All_Users})


@group_required('Administrator', login_url='index')
def show_sales_user(request):
    All_Users = User.objects.filter(groups__id=2)
    return render(request, "adminlte/user/showusers.html", {'All_Users': All_Users})


@group_required('Administrator', login_url='index')
def delete_user(request, id):
    UserInstance = get_object_or_404(User, pk=id)
    if UserInstance:
        UserInstance.delete()
        messages.success(request, 'User Deleted succesfully..')
        return redirect('Showusers')


@group_required(['Administrator'], login_url='index')
def userdetail(request, id):
    try:
        All_Users = User.objects.filter(pk=id)
        User_Under = ParentUser.objects.filter(parent_user_id=id)
        PayOut=Payout.objects.filter(user_id=id)
        print(User_Under)
    except Exception as e:
        All_Users = None

    return render(request, "adminlte/user/showsingleuser.html", {'singleuser': All_Users, 'Related_Users': User_Under,'payout':PayOut})


@group_required(['Administrator','Regional Manager', 'Concierge Manager'], login_url='index')
def userdetail_other(request, id, parent):
    if parent == '0':
        Is_user_under_current_user = ParentUser.objects.filter(
            parent_user_id=request.user.id, current_user_id=id)
        if Is_user_under_current_user:
            try:
                All_Users = User.objects.filter(pk=id)
                User_Under = ParentUser.objects.filter(parent_user_id=id)
                PayOut=Payout.objects.filter(user_id=id)
    
            except Exception as e:
                All_Users = None
        else:
            return HttpResponse('Permission denied')
        return render(request, "adminlte/user/showsingleuser.html", {'singleuser': All_Users, 'Related_Users': User_Under,'payout':PayOut})
    else:
        Is_user_under_current_user = ParentUser.objects.filter(
            parent_user_id=parent, current_user_id=id)
        if Is_user_under_current_user:
            try:
                All_Users = User.objects.filter(pk=id)
                User_Under = ParentUser.objects.filter(parent_user_id=id)
                orders=OrderItem.objects.filter(product__Owner_id=id)
                PayOut=Payout.objects.filter(user_id=id)

            except Exception as e:
                All_Users = None
        else:
            return HttpResponse('Permission denied')
        return render(request, "adminlte/user/showsingleuser.html", {'singleuser': All_Users, 'Related_Users': User_Under,'orders':orders,'payout':PayOut})


@group_required('Administrator', login_url='index')
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_active = False
            user.save()
            # print(request.POST.get('groups'))
            my_group = Group.objects.get(id=request.POST.get('groups'))
            my_group.user_set.add(user)

            # parentuser = UserDetailForm(request.POST)
            ParentUserInstance = ParentUser(current_user=user)
            parentuser = UserDetailForm(
                request.POST, instance=ParentUserInstance)
            if parentuser.is_valid():
                parentuser.save()
            current_site = get_current_site(request)

            to_email = form.cleaned_data.get('email')
            subject, from_email, to = 'Activation of your account at Each Online', 'test@gmail.com', to_email
            text_content = 'Activation of your account at Each Online.'
            html_content = render_to_string('email/client_acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                'password': form.cleaned_data.get('password1'),
            })

            msg = EmailMultiAlternatives(
                subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            messages.success(
                request, 'Email has been sent to user for approval.')
            return redirect('Showusers')
    else:
        form = SignUpForm()
    return render(request, 'adminlte/user/createuser.html', {'form': form})


def client_activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        current_site = get_current_site(request)
        mail_subject = 'Welcome to Each Online'
        message = render_to_string('email/welcome_email.html', {
            'user': user,
            'domain': current_site.domain,
        })
        to_email = user.email
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        email.content_subtype = "html"
        email.send()
        # login(request, user)
        return HttpResponse('Thankyou.')
    else:
        return HttpResponse('Activation link is invalid!')


@group_required('Administrator', login_url='index')
def add_page(request):
    if request.method == 'POST':
        Page_form = PagesForm(request.POST, request.FILES)
        if Page_form.is_valid():
            if request.POST.get('Page_Role') == 'About':
                try:
                    priority = Pages.objects.get(Page_Role='About')
                    priority.Page_Role = 'Content'
                    priority.save()
                except Exception as e:
                    pass
            if request.POST.get('Page_Role') == 'Contact':
                try:
                    priority = Pages.objects.get(Page_Role='Contact')
                    priority.Page_Role = 'Content'
                    priority.save()
                except Exception as e:
                    pass
            if request.POST.get('Page_Role') == 'Privacy':
                try:
                    priority = Pages.objects.get(Page_Role='Privacy')
                    priority.Page_Role = 'Content'
                    priority.save()
                except Exception as e:
                    pass
            if request.POST.get('Page_Role') == 'Partner':
                try:
                    priority = Pages.objects.get(Page_Role='Partner')
                    priority.Page_Role = 'Partner'
                    priority.save()
                except Exception as e:
                    pass
            if request.POST.get('Page_Role') == 'Term':
                try:
                    priority = Pages.objects.get(Page_Role='Term')
                    priority.Page_Role = 'Term'
                    priority.save()
                except Exception as e:
                    pass
            if request.POST.get('Page_Role') == 'Return':
                try:
                    priority = Pages.objects.get(Page_Role='Return')
                    priority.Page_Role = 'Return'
                    priority.save()
                except Exception as e:
                    pass
            Pageform = Page_form.save()
            messages.success(request, 'Page Added succesfully..')
            return redirect('ShowPage')
        else:
            return render(request, "adminlte/Page/create-page.html", {'form': Page_form})
    else:
        return render(request, "adminlte/Page/create-page.html", {'form': PagesForm})


@group_required('Administrator', login_url='index')
def show_page(request):
    try:
        All_Pages = Pages.objects.all()
    except Exception as e:
       All_Pages = False
    return render(request, "adminlte/Page/show-pages.html", {'All_Pages': All_Pages})


@group_required('Administrator', login_url='index')
def single_page(request, id):
    # IsPage=get_object_or_404(Pages,pk=id)
    IsPage = Pages.objects.filter(pk=id)
    return render(request, "adminlte/Page/ShowSinglePage.html", {'SinglePage': IsPage})


@group_required('Administrator', login_url='index')
def delete_single_page(request, id):
    ProjectInstance = get_object_or_404(Pages, pk=id)
    if ProjectInstance:
        messages.success(request, str(
            ProjectInstance.Page_Name)+' Deleted succesfully..')
        ProjectInstance.delete()
        return redirect('ShowPage')


@group_required('Administrator', login_url='index')
def edit_single_page(request, id):
    if request.method == 'POST':
        obj = get_object_or_404(Pages, pk=id)
        if obj:
            Credits_Form = PagesForm(request.POST, request.FILES, instance=obj)
            if Credits_Form.is_valid:
                if request.POST.get('Page_Role') == 'About':
                    try:
                        priority = Pages.objects.get(Page_Role='About')
                        priority.Page_Role = 'Content'
                        priority.save()
                    except Exception as e:
                        pass
                if request.POST.get('Page_Role') == 'Contact':
                    try:
                        priority = Pages.objects.get(Page_Role='Contact')
                        priority.Page_Role = 'Content'
                        priority.save()
                    except Exception as e:
                        pass
                if request.POST.get('Page_Role') == 'Privacy':
                    try:
                        priority = Pages.objects.get(Page_Role='Privacy')
                        priority.Page_Role = 'Content'
                        priority.save()
                    except Exception as e:
                        pass
                if request.POST.get('Page_Role') == 'Partner':
                    try:
                        priority = Pages.objects.get(Page_Role='Partner')
                        priority.Page_Role = 'Partner'
                        priority.save()
                    except Exception as e:
                        pass
                if request.POST.get('Page_Role') == 'Term':
                    try:
                        priority = Pages.objects.get(Page_Role='Term')
                        priority.Page_Role = 'Term'
                        priority.save()
                    except Exception as e:
                        pass
                if request.POST.get('Page_Role') == 'Return':
                    try:
                        priority = Pages.objects.get(Page_Role='Return')
                        priority.Page_Role = 'Return'
                        priority.save()
                    except Exception as e:
                        pass
                Credits_Form.save()
                messages.success(request, str(obj.Page_Name) +
                                 ' Updated succesfully..')
                return redirect('ShowPage')
            else:
                return render(request, 'adminlte/Page/create-page.html', {'form': Credits_Form, 'id': id})
        else:
            raise Http404("No MyModel matches the given query.")
    ProjectInstance = get_object_or_404(Pages, pk=id)
    form = PagesForm(instance=ProjectInstance)
    return render(request, "adminlte/Page/create-page.html", {'form': form, 'id': id})


@group_required(['Administrator', 'SME'], login_url='index')
def show_product(request):
    try:
        if request.user.groups.all()[0].name == 'Administrator':
            All_Products = Product.objects.all()
        elif request.user.groups.all()[0].name == 'SME':
            All_Products = Product.objects.filter(Owner=request.user)
    except Exception as e:
        All_Products = False
    return render(request, "adminlte/product/show-products.html", {'All_Products': All_Products})


@group_required(['Administrator', 'SME'], login_url='index')
def add_product(request):
    if request.method == 'POST':
        Product_Owner_Instance = Product(Owner=request.user)
        product_form = ProductForm(
            request.POST, request.FILES, instance=Product_Owner_Instance)
        if product_form.is_valid():
            productform = product_form.save()
            Product_variant = ProductAttribute(product=productform)
            abc = ProductAttributeForm(
                request.POST, request.FILES, instance=Product_variant)
            if abc.is_valid():
                x = abc.save()
            messages.success(request, 'Product Added succesfully..')
            return redirect('ShowProduct')
        else:
            return render(request, "adminlte/product/create-product.html", {'ProductForm': product_form, })
    else:
        return render(request, "adminlte/product/create-product.html", {'ProductForm': ProductForm, 'variant': ProductAttributeForm})


@group_required(['Administrator', 'SME'], login_url='index')
def single_product(request, id):
    if request.user.groups.all()[0].name == 'admin':
        IsProduct = Product.objects.filter(pk=id)
        variant = ProductAttribute.objects.filter(product_id=id)
    elif request.user.groups.all()[0].name == 'SME':
        Is_user_under_current_user = Product.objects.filter(
            id=id, Owner_id=request.user.id)
        if Is_user_under_current_user:
            IsProduct = Product.objects.filter(Owner=request.user,pk=id)
            variant = ProductAttribute.objects.filter(product_id=id)
        else:
            return HttpResponse('Permission denied...')
    # print(variant)
    return render(request, "adminlte/product/ShowSingleProduct.html", {'Product': IsProduct, 'variantinfo': variant})


@group_required(['Administrator', 'SME'], login_url='index')
def edit_single_product(request, id):
    Is_current_user_Product = Product.objects.filter(
        id=id, Owner_id=request.user.id)
    if Is_current_user_Product:
        if request.method == 'POST':
            obj = get_object_or_404(Product, pk=id)
            if obj:
                Credits_Form = ProductForm(
                    request.POST, request.FILES, instance=obj)
                if Credits_Form.is_valid:
                    Credits_Form.save()
                    messages.success(request, str(
                        obj.Product_Name)+' Updated succesfully..')
                    return redirect('ShowSingleProduct', id)
                else:
                    return render(request, "adminlte/product/create-product.html", {'ProductForm': form, 'ProductDownloadForm': '', 'id': id})
            else:
                raise Http404("No MyModel matches the given query.")
        ProductInstance = get_object_or_404(Product, pk=id)
        form = ProductForm(instance=ProductInstance)
        return render(request, "adminlte/product/create-product.html", {'ProductForm': form, 'ProductDownloadForm': '', 'id': id})
    else:
        raise Http404("No MyModel matches the given query.")


@group_required(['Administrator', 'SME'], login_url='index')
def delete_single_product(request, id):
    ProductInstance = get_object_or_404(Product, pk=id)
    Is_current_user_Product = Product.objects.filter(
        id=id, Owner_id=request.user.id)
    if Is_current_user_Product:
        messages.success(request, str(
            ProductInstance.Product_Name)+' Deleted succesfully..')
        ProductInstance.delete()
        return redirect('ShowProduct')
    else:
        return HttpResponse('Product not related to you...')


@group_required(['Administrator', 'SME'], login_url='index')
def assign_variant(request, id):
    Is_current_user_Product = Product.objects.filter(
        id=id, Owner_id=request.user.id)
    if Is_current_user_Product:
        productinstance = get_object_or_404(Product, pk=id)
        if request.method == 'POST':
            productinstance = get_object_or_404(Product, pk=id)
            Product_variant = ProductAttribute(product=productinstance)
            abc = ProductAttributeForm(
                request.POST, request.FILES, instance=Product_variant)
            if abc.is_valid():
                x = abc.save()
                messages.success(request, 'Variant added sucessfully')
                return redirect('ShowSingleProduct', id)
        # ProductInstance=get_object_or_404(ProductAttribute,product=id)
        # form = ProductAttributeForm(instance=ProductInstance)
        return render(request, "adminlte/product/create-variant.html", {'variant': ProductAttributeForm, 'id': id, 'Productname': productinstance.Product_Name})
    else:
        raise Http404("No MyModel matches the given query.")


@group_required('Administrator', login_url='index')
def add_rate(request):
    if request.method == 'POST':
        rate_form = RateForm(request.POST, request.FILES)
        if rate_form.is_valid():
            productform = rate_form.save()
            messages.success(request, 'Rate Percantage Added succesfully..')
            return redirect('AddNewRate')
        else:
            return render(request, "adminlte/rate/create-rate.html", {'rateform': rate_form})
    else:
        return render(request, "adminlte/rate/create-rate.html", {'rateform': RateForm, 'detail': Credits.objects.all()})


@group_required('Administrator', login_url='index')
def edit_rate(request, id):
    RateInstance = get_object_or_404(Credits, pk=id)
    if request.method == 'POST':
        Credits_Form = RateForm(
            request.POST, request.FILES, instance=RateInstance)
        if Credits_Form.is_valid:
            Credits_Form.save()
            messages.success(request, 'Rate Percantage Updated succesfully..')
            return redirect('AddNewRate')
        else:
            return render(request, "adminlte/rate/create-rate.html", {'rateform': Credits_Form, 'id': id})

    form = RateForm(instance=RateInstance)

    return render(request, "adminlte/rate/create-rate.html", {'rateform': form, 'id': id})


def cartcount(request):
    try:
        currentcart = Cart.objects.get(user_id=request.user.id).pk
        cartitemcount = CartItem.objects.filter(cart_id=currentcart).count()
        cartcount = CartItem.objects.filter(cart_id=currentcart)
        currentUserGroup = request.user.groups.all()[0].name
        data = defaultdict(list)
        i = 0
        for prd in cartcount:
            price = prd.product.Product_Price
            data[i] = [prd.product.id, prd.product.Product_Name, prd.product.Product_Description, prd.product.Product_Price,
                prd.product.Product_Preview_image.name if prd.product.Product_Preview_image else None, prd.id]
            i = i+1
        return JsonResponse({'type': 'addcart', 'status': 'cart', 'cartcount': cartitemcount, 'cartproducts': data}, safe=False)
    except CartItem.DoesNotExist:
        return JsonResponse({'type': 'addcart', 'status': 'cart', 'cartcount': ''}, safe=False)


@csrf_exempt
def CreateCart(request):
    if request.user.is_authenticated:
        if request.is_ajax():
            if request.POST.get('ProductId'):
                ProductInstance = get_object_or_404(
                    Product, pk=request.POST.get('ProductId'))
                price = ProductInstance.Product_Price
                try:
                    CurrentCart = Cart.objects.get(
                        user_id=request.user.id, status='Active')
                    IsProductInCart = CartItem.objects.filter(
                        cart_id=CurrentCart.pk, product=ProductInstance)
                    if IsProductInCart:
                        return JsonResponse({'type': 'addcart1', 'status': 'AlreadyInCart'}, safe=False)
                    else:
                        CartItem.objects.create(
                            product=ProductInstance, price_ht=price, cart=CurrentCart)
                        cartcount = CartItem.objects.filter(
                            cart_id=CurrentCart.pk).count()
                        return JsonResponse({'type': 'addcart2', 'status': 'cart', 'cartcount': cartcount}, safe=False)
                except Cart.DoesNotExist:
                    CurrentCart = None
                    cartint = Cart.objects.create(
                        user=request.user, status='Active')
                    CartItem.objects.create(
                        product=ProductInstance, price_ht=price, cart=cartint)
                    cartcount = CartItem.objects.filter(
                        cart_id=cartint.pk).count()
                    return JsonResponse({'type': 'addcart3', 'status': 'cart', 'cartcount': cartcount}, safe=False)

    return JsonResponse({'type': 'addcart', 'status': request.user.is_authenticated}, safe=False)


@csrf_exempt
def DeleteCartItem(request):
    if request.user.is_authenticated:
        cartitm = get_object_or_404(
            CartItem, pk=request.POST.get('cartitem_id'))
        try:
            Cartitems = CartItem.objects.filter(id=cartitm.pk).delete()
            currentcart = Cart.objects.get(user_id=request.user.id).pk
            cartitemcount = CartItem.objects.filter(
                cart_id=currentcart).count()
            # cartcount = CartItem.objects.filter(cart_id=currentcart)
        except CartItem.DoesNotExist:
            pass
        return JsonResponse({'type': 'DeleteCart', 'status': 'deleted', 'cartcount': cartitemcount}, safe=False)


def wishcount(request):
    try:
        currentwishlist = Wishlist.objects.get(user_id=request.user.id).pk
        wishlistcount = WishlistItem.objects.filter(
            Wishlist_id=currentwishlist).count()
        return JsonResponse({'type': 'wishlistcount', 'status': 'wishlistcount', 'wishlistcount': wishlistcount}, safe=False)

    except CartItem.DoesNotExist:
        return JsonResponse({'type': 'addcart', 'status': 'cart', 'cartcount': ''}, safe=False)


@csrf_exempt
def Wish(request):
    if request.user.is_authenticated:
        if request.is_ajax():
            if request.POST.get('ProductId'):
                Product = get_object_or_404(
                    Products, pk=request.POST.get('ProductId'))
                try:
                    CurrentCart = Wishlist.objects.get(
                        user_id=request.user.id, status='Active')
                    IsProductInCart = WishlistItem.objects.filter(
                        Wishlist_id=CurrentCart.pk, product_id=Product)

                    if IsProductInCart:
                        return JsonResponse({'type': 'addcart1', 'status': 'AlreadyInWishlist'}, safe=False)

                    else:
                        WishlistItem.objects.create(
                            product=Product, Wishlist=CurrentCart)
                        wishlistcount = WishlistItem.objects.filter(
                            Wishlist_id=CurrentCart.pk).count()
                        return JsonResponse({'type': 'addcart2', 'status': 'addedinwishlist', 'wishlistcount': wishlistcount}, safe=False)

                except Wishlist.DoesNotExist:

                    wish = Wishlist.objects.create(
                        user=request.user, status='Active')
                    WishlistItem.objects.create(product=Product, Wishlist=wish)
                    wishlistcount = CartItem.objects.filter(
                        cart_id=wish.pk).count()
                    return JsonResponse({'type': 'Wishlist', 'status': 'addedinwishlist', 'wishlistcount': wishlistcount}, safe=False)

    return JsonResponse({'type': 'addcart', 'status': request.user.is_authenticated}, safe=False)


def Checkout(request):
    if request.user.is_authenticated:
        host = request.get_host()
        try:
            currentcart = Cart.objects.get(user_id=request.user.id).pk
            CartProducts = CartItem.objects.filter(
                cart_id=currentcart).values()
            totalprice = CartItem.objects.filter(
                cart_id=currentcart).aggregate(Sum('price_ht'))
            data = serializers.serialize('json', CartProducts)

        except Cart.DoesNotExist:
            CartProducts = None
        return JsonResponse({CartProducts}, safe=False)
        return render(request, 'frontend/Checkout.html', {'cartproducts': CartProducts, 'totalprice': totalprice['price_ht__sum']})
    return render(request, 'frontend/Checkout.html', {'cartproducts': None})


def productfilter(request):
    searched_companies = Company_details.objects.filter(
        Q(user__is_active=1)
        & Q(user__first_name__icontains=request.GET.get('CompanyName').strip())
        & Q(company_info__icontains=request.GET.get('description').strip())
        & (Q(Zip_code=request.GET.get('postal')) if request.GET.get('postal') else Q(user__is_active=1))
        & (Q(country_id=request.GET.get('country')) if request.GET.get('country') else Q(user__is_active=1))
        & (Q(City_id=request.GET.get('city')) if request.GET.get('city') else Q(user__is_active=1))
    ).exclude(user__first_name__icontains=True, user__first_name='', company_info=True, company_info__contains='', Zip_code='')
    return HttpResponseI('working')


@csrf_exempt
def BuyProductUsingStripe(request):
    if request.user.is_authenticated:
        try:
            currentcart = Cart.objects.get(user_id=request.user.id).pk
            totalprice = CartItem.objects.filter(
                cart_id=currentcart).aggregate(Sum('price_ht'))
            CartProducts = CartItem.objects.filter(cart_id=currentcart)
            token = stripe.Token.create(
                card={
                    "number": request.POST.get('cardnumber'),
                    "exp_month": int(request.POST.get('month')),
                    "exp_year": int(request.POST.get('year')),
                    "cvc": int(request.POST.get('cvv')),
                    "address_city": 'chandigarh',
                    "address_state": 'chandigarh',
                    "address_country": 'India',
                    "address_zip": '160059',
                }
            )
            customer = stripe.Customer.create(
                name='test',
                email='mohitsharma@csgroupchd.com',
                source=token,
                address={
                    "line1": 'chandigarh',
                    "city": 'chandigarh',
                    "state": 'chandigarh',
                    "country": 'India',
                    "postal_code": '160059',
                },

            )

            charge = stripe.Charge.create(
            amount=int(totalprice['price_ht__sum'])*100,
            currency="INR",
            customer=customer.id,
            description='testing',
            # metadata='data',
            )
            # Store data in order table after sucessfull payment
            if charge.status == 'succeeded':
                try:
                    # create new order if order not exist
                    OrderCreated = Order(CustomerId=customer.id, cart_id=currentcart, user_id=request.user.id,
                                         CustomerIdPaymentGateway='Stripe', chargeId=charge.id, currency=charge.currency)
                    OrderCreated.save()
                    # add products from cart to order item
                    for prd in CartProducts:
                        OrderItemCreated = OrderItem(
                            product_id=prd.product.id, Price_Paid=prd.price_ht, order=OrderCreated)
                        try:
                            OrderItemCreated.save()
                            CartItem.objects.filter(
                                cart_id=currentcart).delete()
                        except CartItem.DoesNotExist:
                            pass

                    return ordermail(request, OrderCreated.pk, totalprice['price_ht__sum'])

                    return JsonResponse({'type': 'StripePayment', 'status': 'StripePayment', 'ChargeResponsed': charge, 'CustomerResponse': customer, 'invoice': charge.receipt_url}, safe=False)

                except Order.DoesNotExist:
                    pass

        except Exception as e:
            return HttpResponse(e)


@group_required('SME', login_url='index')
def add_attributelevel(request):
    if request.method == 'POST':
        category_form = AttributeBaseForm(request.POST, request.FILES)
        if category_form.is_valid():
            categoryform = category_form.save()
            messages.success(request, 'Label Added succesfully..')
            return redirect('Showattributelevel')
        else:
            return render(request, "adminlte/product/create-attribute-label.html", {'form': category_form})
    else:
        return render(request, "adminlte/product/create-attribute-label.html", {'form': AttributeBaseForm})


@group_required('SME', login_url='index')
def show_attributelevel(request):
    try:
        All_Categories = AttributeBase.objects.all()
    except Exception as e:
       All_Categories = False
    return render(request, "adminlte/product/show-attribute-label.html", {'All_Categories': All_Categories})


@group_required('SME', login_url='index')
def edit_attributelevel(request, id):
    if request.method == 'POST':
        obj = get_object_or_404(Categories, pk=id)
        if obj:
            Credits_Form = CategoryForm(
                request.POST, request.FILES, instance=obj)
            if Credits_Form.is_valid:
                Credits_Form.save()
                messages.success(request, str(
                    obj.Category_Name)+' Updated succesfully..')
                return redirect('ShowProductCategory')
            else:
                return render(request, "adminlte/product/create-attribute-label.html", {'form': Credits_Form, 'id': id})
        else:
            raise Http404("No MyModel matches the given query.")
    ProjectInstance = get_object_or_404(Categories, pk=id)
    form = CategoryForm(instance=ProjectInstance)
    return render(request, "adminlte/product/create-attribute-label.html", {'form': form, 'id': id})


@group_required('SME', login_url='index')
def delete_attributelevel(request, id):
    ProjectInstance = get_object_or_404(Categories, pk=id)
    if ProjectInstance:
        messages.success(request, str(
            ProjectInstance.Category_Name)+' Deleted succesfully..')
        ProjectInstance.delete()
        return redirect('ShowProductCategory')


@group_required('Administrator', login_url='index')
def add_attributeproperty(request):
    if request.method == 'POST':
        category_form = AttributeForm(request.POST, request.FILES)
        if category_form.is_valid():
            categoryform = category_form.save()
            messages.success(request, 'Label Added succesfully..')
            return redirect('Showattributeproperty')
        else:
            return render(request, "adminlte/product/create-attribute-property.html", {'form': category_form})
    else:
        return render(request, "adminlte/product/create-attribute-property.html", {'form': AttributeForm})


@group_required('Administrator', login_url='index')
def show_attributeproperty(request):
    try:
        All_Categories = Attribute.objects.all()
    except Exception as e:
       All_Categories = False
    return render(request, "adminlte/product/show-attribute-property.html", {'All_Categories': All_Categories})


@group_required('Administrator', login_url='index')
def edit_attributeproperty(request, id):
    if request.method == 'POST':
        obj = get_object_or_404(Categories, pk=id)
        if obj:
            Credits_Form = CategoryForm(
                request.POST, request.FILES, instance=obj)
            if Credits_Form.is_valid:
                Credits_Form.save()
                messages.success(request, str(
                    obj.Category_Name)+' Updated succesfully..')
                return redirect('ShowProductCategory')
            else:
                return render(request, "adminlte/product/create-attribute-property.html", {'form': Credits_Form, 'id': id})
        else:
            raise Http404("No MyModel matches the given query.")
    ProjectInstance = get_object_or_404(Categories, pk=id)
    form = CategoryForm(instance=ProjectInstance)
    return render(request, "adminlte/product/create-attribute-property.html", {'form': form, 'id': id})


@group_required('Administrator', login_url='index')
def delete_attributeproperty(request, id):
    ProjectInstance = get_object_or_404(Categories, pk=id)
    if ProjectInstance:
        messages.success(request, str(
            ProjectInstance.Category_Name)+' Deleted succesfully..')
        ProjectInstance.delete()
        return redirect('ShowProductCategory')


def totalprice(request):
    stripe.api_key = 'sk_test_51HTt4sJOxKwQ6C0za7HJmwXzzPbGQah2NpyQsVdLCmk1dQgfrjGZ9u7ec5CqDeTBX70j3Ghu7x6fF6M5S6tloClU00p11VH5k0'
    try:
        customer = stripe.Customer.create(
            name='test',
            email=request.user.email,
        )
        currentcart = Cart.objects.get(user_id=request.user.id).pk
        totalprice = CartItem.objects.filter(
            cart_id=currentcart).aggregate(Sum('price_ht'))
        CartProducts = CartItem.objects.filter(cart_id=currentcart)
        currentuser = ''
        price = 0
        for cartdata in CartProducts:
            if cartdata.product_variant:
                productattrprice = ProductAttribute.objects.get(
                    attribute_ptr_id=cartdata.product_variant)
                price += productattrprice.price if productattrprice.price else 0
                price += productattrprice.Shipping if productattrprice.Shipping else 0
            else:
                price += cartdata.product.Product_Price if cartdata.product.Product_Price else 0
                price += cartdata.product.Product_Shipping if cartdata.product.Product_Shipping else 0
        return JsonResponse({'price': price, 'customer': customer}, safe=False)
    except Exception as e:
        return HttpResponse(e)


def paystripe(request):
    stripe.api_key = 'sk_test_51HTt4sJOxKwQ6C0za7HJmwXzzPbGQah2NpyQsVdLCmk1dQgfrjGZ9u7ec5CqDeTBX70j3Ghu7x6fF6M5S6tloClU00p11VH5k0'
    response = stripe.OAuth.token(
        grant_type='authorization_code',
        code=request.GET.get('code'),
    )
    connected_account_id = ''
    # Access the connected account id in the response
    connected_account_id = response['stripe_user_id']
    print(connected_account_id)
    try:
        Current_User = ParentUser.objects.get(current_user_id=request.user.id)
        Current_User.stripe_connect = connected_account_id
        Current_User.save()
    except ParentUser.DoesNotExist:
        Current_User = ParentUser(
            current_user_id=request.user.id, stripe_connect=connected_account_id)
        Current_User.save()
    messages.success(request, 'Stripe account linked succesfully.')
    return HttpResponse(connected_account_id)


def paytostripe(request):
    stripe.api_key = 'sk_test_51HTt4sJOxKwQ6C0za7HJmwXzzPbGQah2NpyQsVdLCmk1dQgfrjGZ9u7ec5CqDeTBX70j3Ghu7x6fF6M5S6tloClU00p11VH5k0'
    try:
        Rate = Credits.objects.all()
        Manager_Rate = ''
        Con_Manager = ''
        Sme_Rate = ''
        for rate in Rate:
            Manager_Rate = rate.Manager_Rate
            Con_Manager = rate.Manufacturer_Rate
            Sme_Rate = rate.Sme_Rate

        currentcart = Cart.objects.get(user_id=request.user.id).pk
        totalprice = CartItem.objects.filter(
            cart_id=currentcart).aggregate(Sum('price_ht'))
        CartProducts = CartItem.objects.filter(cart_id=currentcart)
        data = defaultdict(list)
        currentuser = ''
        price=0
        for cartdata in CartProducts:

            if cartdata.product.Owner.id == currentuser:
                print('2', cartdata)
                price += cartdata.product.Product_Price if cartdata.product.Product_Price else 0
                price += cartdata.product.Product_Shipping if cartdata.product.Product_Shipping else 0
                # data[cartdata.product.Owner.id] = price
            else:
                currentuser = ''
                print('1', cartdata)
                currentuser = cartdata.product.Owner.id

                if cartdata.product_variant:
                    productattrprice = ProductAttribute.objects.get(attribute_ptr_id=cartdata.product_variant)
                    price+= productattrprice.price if productattrprice.price else 0 
                    price+=productattrprice.Shipping if productattrprice.Shipping else 0
                else:
                    price += cartdata.product.Product_Price if cartdata.product.Product_Price else 0
                    price += cartdata.product.Product_Shipping if cartdata.product.Product_Shipping else 0

            stripeaccount = ''
            data[cartdata.product.Owner.id] = price

        alldata = dict(data)
        print(alldata)
        
        for k in alldata:
            return HttpResponse(k)

            total_price = alldata[k]

            GetSmeAmount = total_price*Sme_Rate/100
            GetManagerAmount = total_price*Manager_Rate/100
            GetConManagerAmount = total_price*Con_Manager/100

            Sme_Stripe = ParentUser.objects.get(current_user_id=k)
            Sme_Stripe_Connect = Sme_Stripe.stripe_connect

            Conceirge_Stripe = ParentUser.objects.get(
                current_user_id=Sme_Stripe.parent_user_id)
            Conceirge_Stripe_Connect = Conceirge_Stripe.stripe_connect

            Manager_Stripe = ParentUser.objects.get(
                current_user_id=Conceirge_Stripe.parent_user_id)
            Manager_Stripe_Connect = Manager_Stripe.stripe_connect

            print(Sme_Stripe_Connect)

            transfer1 = stripe.Transfer.create(
                amount=int(GetSmeAmount)*100,
                currency='usd',
                destination=Sme_Stripe_Connect,
                transfer_group='{ORDER10}',
            )

            transfer2 = stripe.Transfer.create(
                amount=int(GetManagerAmount)*100,
                currency='usd',
                destination=Manager_Stripe_Connect,
                transfer_group='{ORDER10}',
            )

            transfer3 = stripe.Transfer.create(
                amount=int(GetConManagerAmount)*100,
                currency='usd',
                destination=Conceirge_Stripe_Connect,
                transfer_group='{ORDER10}',
            )

        try:
            # create new order if order not exist
            OrderCreated = Order(CustomerId=customer.id, cart_id=currentcart, user_id=request.user.id,
                                 CustomerIdPaymentGateway='Stripe', chargeId=charge.id, currency=charge.currency)
            OrderCreated.save()
            # add products from cart to order item
            for prd in CartProducts:
                OrderItemCreated = OrderItem(product=prd.product, Price_Paid=prd.product.Product_Price,
                                             product_variant=prd.product_variant if prd.product_variant else None, order=OrderCreated)
                OrderItemCreated.save()

            CartItem.objects.filter(cart_id=currentcart).delete()

            return JsonResponse({'type': 'StripePayment', 'status': 'StripePayment', 'ChargeResponsed': charge, 'CustomerResponse': customer, 'invoice': charge.receipt_url}, safe=False)

        except Order.DoesNotExist:
            pass

            return HttpResponse(total_price)
            print(alldata[k])

        return JsonResponse({'type': 'StripePayment', 'status': 'StripePayment', 'ChargeResponsed': data}, safe=False)
    except Exception as e:
        return HttpResponse(e)


def upload_csv(request):
    varfile = request.FILES['csv_file'] 
    decoded_file = varfile.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_file)
    i=0
    for fields in reader:
        
        # if i == 6:
        #     return HttpResponse('fields')
        if i > 892:
            try:
                
                
                data_dict={}
                
                data_dict["Product_Name"]=fields['name'] if fields['name'] else '' 
                data_dict["Product_Brand"]=fields['Brand'] if fields['Brand'] else '' 
                data_dict["Product_Color"]=fields['color'] if fields['color'] else ''
                data_dict["Product_Connectivity"]=fields['Connectivity'] if fields['Connectivity'] else ''
                data_dict["Product_Price"]=fields['price1'].replace("$", "") if fields['price1'] else '' 
                data_dict["Product_Shipping"]=fields['shipping1'].replace("$", "") if fields['shipping1'] else ''
                data_dict["Product_TextDescription"]=fields['description-text11'] if fields['description-text11'] else ''
                data_dict["Product_Description"]=fields['description-html11'] if fields['description-html11'] else ''
                data_dict["Product_Tag"]=fields['tags']if fields['tags'] else ''
                data_dict["Product_Size"]=fields['size']if fields['size'] else ''
                data_dict["quantity"]=fields['availibilityCount']if fields['availibilityCount'] else ''
                data_dict["Status"]=1
                data_dict["Category"]=20
                
                try:
                    prd=Product(Owner_id=31,Category_id=20)
                    # prd=Product(Owner_id=19,Category_id=1)
                    form=ProductForm(data_dict,instance=prd)
                    if form.is_valid():
                        pid=form.save()	
                        image_urls = [fields['images_big'] if fields['images_big'] else 'https://i.ebayimg.com/images/g/d5UAAOSwoZte8-iW/s-l640.jpg']

                        for image_url in image_urls:
                            # Steam the image from the url
                            request = requests.get(image_url, stream=True)

                            # Was the request OK?
                            if request.status_code != requests.codes.ok:
                                # Nope, error handling, skip file etc etc etc
                                continue
                            
                            # Get the filename from the url, used for saving later
                            file_name = image_url.split('/')[-1]
                            
                            # Create a temporary file
                            lf = tempfile.NamedTemporaryFile()

                            # Read the streamed image in sections
                            for block in request.iter_content(1024 * 8):
                                
                                # If no more file then stop
                                if not block:
                                    break

                                # Write image block to temporary file
                                lf.write(block)

                            # Create the model you want to save the image to
                            image = Product.objects.get(id=pid.pk)
                            # print(file_name)
                            # Save the temporary image to the model#
                            # This saves the model so be sure that is it valid
                            image.Product_Preview_image.save(file_name, files.File(lf))

                            image_urls = [fields['images_big2']  ,fields['images0']  ,fields['image00'] ,fields['images000']  ,fields['image_big00'] ,fields['images_2'] ,fields['images3']  ,fields['images4']  ,fields['images5']]

                            for image_url in image_urls:

                                if image_url:
                                    # Steam the image from the url
                                    request = requests.get(image_url, stream=True)

                                    # Was the request OK?
                                    if request.status_code != requests.codes.ok:
                                        # Nope, error handling, skip file etc etc etc
                                        continue
                                    
                                    # Get the filename from the url, used for saving later
                                    file_name = image_url.split('/')[-1]
                                    
                                    # Create a temporary file
                                    lf = tempfile.NamedTemporaryFile()

                                    # Read the streamed image in sections
                                    for block in request.iter_content(1024 * 8):
                                        
                                        # If no more file then stop
                                        if not block:
                                            break

                                        # Write image block to temporary file
                                        lf.write(block)

                                    # Create the model you want to save the image to
                                    image2 = ProductGallery.objects.create(product_id=pid.pk)
                                    # print(file_name)
                                    # Save the temporary image to the model#
                                    # This saves the model so be sure that is it valid
                                    image2.Product_gallery.save(file_name, files.File(lf))
                                else:
                                    pass
                                                                
                    else:
                        logging.getLogger("error_logger").error(form.errors.as_json())												
                except Exception as e:
                    logging.getLogger("error_logger").error(repr(e))					
                    pass
            except IndexError as e:
                pass
        i=i+1 
    return HttpResponse('gg')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


@group_required('Administrator', login_url='index')
def allorder(request):
    orders=Order.objects.all()
    return render(request, "adminlte/product/orders.html", {'orders': orders})


def singleorder(request,id):
    orders=OrderItem.objects.filter(order_id=id)
    return render(request, "adminlte/product/Single-order.html", {'orders': orders})

@group_required('SME', login_url='index')
def allsmeorder(request):
    try:
        orders=OrderItem.objects.filter(product__Owner_id=request.user.id)
    except Exception as e:
        orders=None
    return render(request, "adminlte/product/Single-order.html", {'orders': orders})



@group_required('Administrator', login_url='index')
def allpayout(request):
    Pays=Payout.objects.all()
    return render(request, "adminlte/product/payout.html", {'Pays': Pays})

 
@group_required(['Regional Manager','Concierge Manager'], login_url='index')
def ShowPayoutToManager(request):
    Pays=Payout.objects.filter(user_id__in=ParentUser.objects.filter(
            parent_user_id=request.user.id).values_list('current_user_id'))
    return render(request, "adminlte/product/payout.html", {'Pays': Pays})