from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from kuangcang.models import Kanche, Caozuo
from datetime import datetime


class RenzhengBaohuzhao(MiddlewareMixin):
    """认证保护罩中间件"""
    
    BAIMING_LUJING = [
        '/denglu/xianshi/',
        '/denglu/tijiao/',
        '/denglu/likakai/',
        '/denglu/yanzhengma/',
        '/jingdian/',
        '/yuanshi/',
    ]
    
    def process_request(self, qingqiu):
        dangqian_lujing = qingqiu.path
        
        for baiming in self.BAIMING_LUJING:
            if dangqian_lujing.startswith(baiming):
                return None
        
        kanche_id = qingqiu.session.get('kanche_bianhao')
        
        if not kanche_id:
            if qingqiu.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'zhuangtai_ma': 'weirenzheng',
                    'tishi_xinxi': '请先进行身份验证'
                }, status=401)
            return redirect(reverse('denglu_xianshi'))
        
        try:
            kanche_duixiang = Kanche.objects.get(
                kanche_bianhao=kanche_id,
                huodong_zhuangtai=168
            )
            qingqiu.kanche = kanche_duixiang
            qingqiu.session['xingtiao_shijian'] = datetime.now().isoformat()
        except Kanche.DoesNotExist:
            qingqiu.session.flush()
            return redirect(reverse('denglu_xianshi'))
        
        return None


class QuanxianJianhuqi(MiddlewareMixin):
    """权限监护器中间件"""
    
    MIANYIJIAN_QUYU = ['/denglu/', '/zhongxin/', '/jingdian/', '/yuanshi/']
    
    def process_request(self, qingqiu):
        dangqian_lujing = qingqiu.path
        
        for quyu in self.MIANYIJIAN_QUYU:
            if dangqian_lujing.startswith(quyu):
                return None
        
        kanche = getattr(qingqiu, 'kanche', None)
        if not kanche:
            return None
        
        return None


class CaozuoJiluqi(MiddlewareMixin):
    """操作记录器中间件"""
    
    JIANSHI_FANGFA = ['POST', 'PUT', 'DELETE', 'PATCH']
    
    def process_response(self, qingqiu, xiangying):
        if qingqiu.method not in self.JIANSHI_FANGFA:
            return xiangying
        
        kanche = getattr(qingqiu, 'kanche', None)
        if not kanche:
            return xiangying
        
        zhuanfa_lian = qingqiu.META.get('HTTP_X_FORWARDED_FOR')
        laiyuan_ip = (zhuanfa_lian.split(',')[0] 
                     if zhuanfa_lian 
                     else qingqiu.META.get('REMOTE_ADDR', 'weizhi'))
        
        lujing = qingqiu.path
        mokuai = lujing.split('/')[1] if len(lujing.split('/')) > 1 else 'zhuye'
        
        try:
            Caozuo.objects.create(
                kanche_yinyong=kanche,
                mokuai_mingcheng=mokuai,
                caozuo_leixing=qingqiu.method,
                caozuo_miaoshu=f"{qingqiu.method}请求于{lujing}",
                qingqiu_fangshi=qingqiu.method,
                qingqiu_lujing=lujing,
                qingqiu_ip=laiyuan_ip
            )
        except Exception:
            pass
        
        return xiangying
