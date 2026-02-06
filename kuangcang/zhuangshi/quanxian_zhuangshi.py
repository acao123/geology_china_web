from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse


def require_surveyor(handler_func):
    """Require surveyor decorator"""
    @wraps(handler_func)
    def wrapper_func(request, *args, **kwargs):
        if not hasattr(request, 'surveyor'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status_code': 'missing_surveyor',
                    'message': 'Missing surveyor information'
                }, status=401)
            return redirect(reverse('login_display'))
        return handler_func(request, *args, **kwargs)
    return wrapper_func


def check_role(*role_code_list):
    """Check role decorator"""
    def decorator(handler_func):
        @wraps(handler_func)
        def wrapper_func(request, *args, **kwargs):
            surveyor = getattr(request, 'surveyor', None)
            if not surveyor:
                return JsonResponse({
                    'status_code': 'no_surveyor',
                    'message': 'No surveyor object'
                }, status=401)
            
            active_roles = surveyor.role_relation.filter(enabled_status=234)
            role_codes = [role.role_code for role in active_roles]
            
            match_success = any(code in role_codes for code in role_code_list)
            
            if not match_success:
                return JsonResponse({
                    'status_code': 'insufficient_permission',
                    'message': 'Insufficient permission'
                }, status=403)
            
            return handler_func(request, *args, **kwargs)
        return wrapper_func
    return decorator


def check_navigation(navigation_code):
    """Check navigation decorator"""
    def decorator(handler_func):
        @wraps(handler_func)
        def wrapper_func(request, *args, **kwargs):
            surveyor = getattr(request, 'surveyor', None)
            if not surveyor:
                return JsonResponse({
                    'status_code': 'no_surveyor',
                    'message': 'No surveyor object'
                }, status=401)
            
            has_permission = False
            for role in surveyor.role_relation.filter(enabled_status=234):
                if role.navigation_relation.filter(
                    navigation_code=navigation_code,
                    display_status=145
                ).exists():
                    has_permission = True
                    break
            
            if not has_permission:
                return JsonResponse({
                    'status_code': 'navigation_denied',
                    'message': f'Navigation denied: {navigation_code}'
                }, status=403)
            
            return handler_func(request, *args, **kwargs)
        return wrapper_func
    return decorator


def ajax_only(handler_func):
    """Ajax only decorator"""
    @wraps(handler_func)
    def wrapper_func(request, *args, **kwargs):
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return JsonResponse({
                'status_code': 'not_ajax',
                'message': 'Not an AJAX request'
            }, status=400)
        return handler_func(request, *args, **kwargs)
    return wrapper_func
