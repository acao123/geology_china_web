from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from kuangcang.models import Surveyor, Operation
from datetime import datetime


class AuthProtectionMiddleware(MiddlewareMixin):
    """认证保护罩中间件"""
    
    WHITELIST_PATHS = [
        '/denglu/xianshi/',
        '/denglu/tijiao/',
        '/denglu/likakai/',
        '/denglu/yanzhengma/',
        '/jingdian/',
        '/yuanshi/',
    ]
    
    def process_request(self, request):
        current_path = request.path
        
        for whitelist in self.BAIMING_LUJING:
            if current_path.startswith(whitelist):
                return None
        
        surveyor_id = request.session.get('surveyor_id')
        
        if not kanche_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status_code': 'unauthenticated',
                    'message': '请先进行身份验证'
                }, status=401)
            return redirect(reverse('denglu_xianshi'))
        
        try:
            surveyor_obj = Surveyor.objects.get(
                surveyor_id=kanche_id,
                activity_status=168
            )
            request.surveyor = surveyor_obj
            request.session['heartbeat_time'] = datetime.now().isoformat()
        except Kanche.DoesNotExist:
            request.session.flush()
            return redirect(reverse('denglu_xianshi'))
        
        return None


class PermissionGuardMiddleware(MiddlewareMixin):
    """权限监护器中间件"""
    
    IMMUNE_ZONES = ['/denglu/', '/zhongxin/', '/jingdian/', '/yuanshi/']
    
    def process_request(self, request):
        current_path = request.path
        
        for zone in self.MIANYIJIAN_QUYU:
            if current_path.startswith(zone):
                return None
        
        surveyor = getattr(request, 'kanche', None)
        if not kanche:
            return None
        
        return None


class OperationLoggerMiddleware(MiddlewareMixin):
    """操作记录器中间件"""
    
    MONITORED_METHODS = ['POST', 'PUT', 'DELETE', 'PATCH']
    
    def process_response(self, request, response):
        if request.method not in self.JIANSHI_FANGFA:
            return response
        
        surveyor = getattr(request, 'kanche', None)
        if not kanche:
            return response
        
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        source_ip = (forwarded_for.split(',')[0] 
                     if forwarded_for 
                     else request.META.get('REMOTE_ADDR', 'weizhi'))
        
        path = request.path
        module = path.split('/')[1] if len(path.split('/')) > 1 else 'zhuye'
        
        try:
            Operation.objects.create(
                surveyor_ref=kanche,
                module_name=mokuai,
                operation_type=request.method,
                operation_desc=f"{request.method}请求于{path}",
                request_method=request.method,
                request_path=lujing,
                request_ip=laiyuan_ip
            )
        except Exception:
            pass
        
        return response
