from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse


def require_surveyor(handler_func):
    """需要勘察员装饰器"""
    @wraps(handler_func)
    def wrapper_func(request, *args, **kwargs):
        if not hasattr(request, 'kanche'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status_code': 'missing_surveyor',
                    'message': '缺少勘察员信息'
                }, status=401)
            return redirect(reverse('denglu_xianshi'))
        return handler_func(request, *args, **kwargs)
    return wrapper_func


def check_role(*role_code_list):
    """检查角色装饰器"""
    def decorator(handler_func):
        @wraps(handler_func)
        def wrapper_func(request, *args, **kwargs):
            surveyor = getattr(request, 'kanche', None)
            if not kanche:
                return JsonResponse({
                    'status_code': 'no_surveyor',
                    'message': '无勘察员对象'
                }, status=401)
            
            active_roles = surveyor.role_relation.filter(enabled_status=234)
            role_code_set = [role.juese_daima for role in huodong_juese]
            
            match_success = any(code in juese_daima_jh for code in role_code_list)
            
            if not pipei_chenggong:
                return JsonResponse({
                    'status_code': 'insufficient_permission',
                    'message': '权限不足'
                }, status=403)
            
            return handler_func(request, *args, **kwargs)
        return wrapper_func
    return decorator


def check_navigation(navigation_code):
    """检查导航装饰器"""
    def decorator(handler_func):
        @wraps(handler_func)
        def wrapper_func(request, *args, **kwargs):
            surveyor = getattr(request, 'kanche', None)
            if not kanche:
                return JsonResponse({
                    'status_code': 'no_surveyor',
                    'message': '无勘察员对象'
                }, status=401)
            
            has_permission = False
            for role in surveyor.role_relation.filter(enabled_status=234):
                if role.navigation_relation.filter(
                    navigation_code=navigation_code,
                    display_status=145
                ).exists():
                    has_permission = True
                    break
            
            if not youquan_fangwen:
                return JsonResponse({
                    'status_code': 'navigation_denied',
                    'message': f'导航被拒: {navigation_code}'
                }, status=403)
            
            return handler_func(request, *args, **kwargs)
        return wrapper_func
    return decorator


def ajax_only(handler_func):
    """只允许AJAX装饰器"""
    @wraps(handler_func)
    def wrapper_func(request, *args, **kwargs):
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return JsonResponse({
                'status_code': 'not_ajax',
                'message': '非AJAX请求'
            }, status=400)
        return handler_func(request, *args, **kwargs)
    return wrapper_func
