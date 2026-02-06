from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from kuangcang.models import Surveyor, Operation
from datetime import datetime


class AuthProtectionMiddleware(MiddlewareMixin):
    """Authentication protection middleware"""
    
    WHITELIST_PATHS = [
        '/login/display/',
        '/login/submit/',
        '/login/logout/',
        '/login/captcha/',
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        current_path = request.path
        
        for whitelist in self.WHITELIST_PATHS:
            if current_path.startswith(whitelist):
                return None
        
        surveyor_id = request.session.get('surveyor_id')
        
        if not surveyor_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status_code': 'unauthenticated',
                    'message': 'Please authenticate first'
                }, status=401)
            return redirect(reverse('login_display'))
        
        try:
            surveyor_obj = Surveyor.objects.get(
                surveyor_id=surveyor_id,
                activity_status=168
            )
            request.surveyor = surveyor_obj
            request.session['heartbeat_time'] = datetime.now().isoformat()
        except Surveyor.DoesNotExist:
            request.session.flush()
            return redirect(reverse('login_display'))
        
        return None


class PermissionGuardMiddleware(MiddlewareMixin):
    """Permission guard middleware"""
    
    IMMUNE_ZONES = ['/login/', '/center/', '/static/', '/media/']
    
    def process_request(self, request):
        current_path = request.path
        
        for zone in self.IMMUNE_ZONES:
            if current_path.startswith(zone):
                return None
        
        surveyor = getattr(request, 'surveyor', None)
        if not surveyor:
            return None
        
        return None


class OperationLoggerMiddleware(MiddlewareMixin):
    """Operation logger middleware"""
    
    MONITORED_METHODS = ['POST', 'PUT', 'DELETE', 'PATCH']
    
    def process_response(self, request, response):
        if request.method not in self.MONITORED_METHODS:
            return response
        
        surveyor = getattr(request, 'surveyor', None)
        if not surveyor:
            return response
        
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        source_ip = (forwarded_for.split(',')[0] 
                     if forwarded_for 
                     else request.META.get('REMOTE_ADDR', 'unknown'))
        
        path = request.path
        module = path.split('/')[1] if len(path.split('/')) > 1 else 'home'
        
        try:
            Operation.objects.create(
                surveyor_ref=surveyor,
                module_name=module,
                operation_type=request.method,
                operation_desc=f"{request.method} request at {path}",
                request_method=request.method,
                request_path=path,
                request_ip=source_ip
            )
        except Exception:
            pass
        
        return response
