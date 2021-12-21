from django import template
import datetime
register = template.Library()
from backend.models import *
from django.db.models import Count, Case, When, IntegerField
from django.http import JsonResponse




@register.simple_tag
def filesize():
    """Returns the filesize of the filename given in value"""
    return 'value'
@register.simple_tag
def megamenu():
    categories=Categories.objects.all()
    return categories

@register.simple_tag
def company(user):
    
    print(user)
    try:
        stripeid=ParentUser.objects.get(current_user=user).stripe_connect
        print('yes')
        
    except Exception as e:
        print(e)
        return None
    return stripeid





    








