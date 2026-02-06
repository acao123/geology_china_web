from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse


def xuyao_kanche(chuli_hanshu):
    """需要勘察员装饰器"""
    @wraps(chuli_hanshu)
    def baozhuang_hanshu(qingqiu, *args, **kwargs):
        if not hasattr(qingqiu, 'kanche'):
            if qingqiu.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'zhuangtai_ma': 'queshao_kanche',
                    'tishi_xinxi': '缺少勘察员信息'
                }, status=401)
            return redirect(reverse('denglu_xianshi'))
        return chuli_hanshu(qingqiu, *args, **kwargs)
    return baozhuang_hanshu


def jiancha_juese(*juese_daima_list):
    """检查角色装饰器"""
    def zhuangshiqi(chuli_hanshu):
        @wraps(chuli_hanshu)
        def baozhuang_hanshu(qingqiu, *args, **kwargs):
            kanche = getattr(qingqiu, 'kanche', None)
            if not kanche:
                return JsonResponse({
                    'zhuangtai_ma': 'wukanche',
                    'tishi_xinxi': '无勘察员对象'
                }, status=401)
            
            huodong_juese = kanche.juese_guanlian.filter(qiyong_zhuangtai=234)
            juese_daima_jh = [juese.juese_daima for juese in huodong_juese]
            
            pipei_chenggong = any(daima in juese_daima_jh for daima in juese_daima_list)
            
            if not pipei_chenggong:
                return JsonResponse({
                    'zhuangtai_ma': 'quanxian_buzu',
                    'tishi_xinxi': '权限不足'
                }, status=403)
            
            return chuli_hanshu(qingqiu, *args, **kwargs)
        return baozhuang_hanshu
    return zhuangshiqi


def jiancha_daohang(daohang_bianma):
    """检查导航装饰器"""
    def zhuangshiqi(chuli_hanshu):
        @wraps(chuli_hanshu)
        def baozhuang_hanshu(qingqiu, *args, **kwargs):
            kanche = getattr(qingqiu, 'kanche', None)
            if not kanche:
                return JsonResponse({
                    'zhuangtai_ma': 'wukanche',
                    'tishi_xinxi': '无勘察员对象'
                }, status=401)
            
            youquan_fangwen = False
            for juese in kanche.juese_guanlian.filter(qiyong_zhuangtai=234):
                if juese.daohang_guanlian.filter(
                    daohang_bianma=daohang_bianma,
                    xianshi_zhuangtai=145
                ).exists():
                    youquan_fangwen = True
                    break
            
            if not youquan_fangwen:
                return JsonResponse({
                    'zhuangtai_ma': 'daohang_jujue',
                    'tishi_xinxi': f'导航被拒: {daohang_bianma}'
                }, status=403)
            
            return chuli_hanshu(qingqiu, *args, **kwargs)
        return baozhuang_hanshu
    return zhuangshiqi


def zhiyun_ajax(chuli_hanshu):
    """只允许AJAX装饰器"""
    @wraps(chuli_hanshu)
    def baozhuang_hanshu(qingqiu, *args, **kwargs):
        if qingqiu.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return JsonResponse({
                'zhuangtai_ma': 'feiajax',
                'tishi_xinxi': '非AJAX请求'
            }, status=400)
        return chuli_hanshu(qingqiu, *args, **kwargs)
    return baozhuang_hanshu
