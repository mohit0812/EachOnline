from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.models import User , Group 
from backend.models import *
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
import six
from django.core.exceptions import PermissionDenied






def GetHeaderContent():
    content = Pages.objects.all()
    return content

def notvisitor(function):
    def wrap(request, args, *kwargs):
        if request.user.groups.filter(id=5):
            return function(request, args, *kwargs)
        else:
            raise PermissionDenied
    wrap.__doc_ = function.__doc_
    wrap.__name_ = function.__name_
    return wrap   


def group_required(group, login_url=None, raise_exception=False):
    """
    Decorator for views that checks whether a user has a group permission,
    redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_perms(user):
        if isinstance(group, six.string_types):
            groups = (group, )
        else:
            groups = group
        # First check if the user has the permission (even anon users)

        if user.groups.filter(name__in=groups).exists():
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_perms, login_url=login_url)








