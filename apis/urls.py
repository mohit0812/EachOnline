from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('products/', views.get_products, name='get_products'),
    path('categories/', views.get_categories, name='get_categories'),
    path('change/password/', views.change_password, name='change_password'),
    path('update/profile/', views.update_profile, name='update_profile'),
    path('current/user/', views.get_currentuser, name='get_currentuser'),
    path('user/billing/address/', views.user_billing_address, name='user_billing_address'),
    path('user/shipping/address/', views.user_shipping_address, name='user_billing_address'),
    path('product/<productId>/', views.get_product, name='get_product'),
    path('create/cart/', views.CreateCart, name='CreateCart'),
    path('remove/cart/', views.removeFromCart, name='removeFromCart'),
    path('page/<role>/', views.getPages, name='getPages'),
    path('wishlist/', views.CreateWishList, name='CreateWishList'),
    path('checkout/', views.CheckOut, name='checkout'),
    path('products/search/', views.SearchProduct, name='SearchProduct'),
    path('payment/done/', views.paymentStripeDone, name='paymentStripeDone'),
    path('orders/history/', views.ordersList, name='ordersList'),
]
