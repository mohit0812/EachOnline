def login_check(view_func):
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated():
            print("yesss")
            return view_func(request, *args, **kwargs)
    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap