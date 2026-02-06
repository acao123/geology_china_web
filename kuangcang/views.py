from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import datetime
from kuangcang.models import Kanche, Juese, Daohang, Caozuo
from kuangcang.yanzhengma_gongju import chuangjian_yanzhengma
from kuangcang.zhuangshi.quanxian_zhuangshi import xuyao_kanche
import json


def denglu_xianshi(qingqiu):
    """登录显示页面"""
    if qingqiu.session.get('kanche_bianhao'):
        return redirect(reverse('zhongxin_xianshi'))
    return render(qingqiu, 'denglu/xianshi.html')


@require_http_methods(["POST"])
def denglu_tijiao(qingqiu):
    """登录提交处理"""
    denglu_biaoshi = qingqiu.POST.get('denglu_biaoshi', '').strip()
    mima_neirong = qingqiu.POST.get('mima_neirong', '').strip()
    yanzhengma_shuru = qingqiu.POST.get('yanzhengma_shuru', '').strip().upper()
    
    huihua_yanzhengma = qingqiu.session.get('yanzhengma_mima', '').upper()
    if not huihua_yanzhengma or yanzhengma_shuru != huihua_yanzhengma:
        return JsonResponse({
            'zhuangtai_ma': 'yanzhengma_cuowu',
            'tishi_xinxi': '验证码输入错误'
        })
    
    qingqiu.session.pop('yanzhengma_mima', None)
    
    if not denglu_biaoshi or not mima_neirong:
        return JsonResponse({
            'zhuangtai_ma': 'xinxi_buquan',
            'tishi_xinxi': '登录信息不完整'
        })
    
    try:
        kanche_duixiang = Kanche.objects.get(denglu_biaoshi=denglu_biaoshi)
        
        if not kanche_duixiang.shifou_huodong():
            return JsonResponse({
                'zhuangtai_ma': 'zhanghu_fengjie',
                'tishi_xinxi': '账户已被封存'
            })
        
        if not kanche_duixiang.yanzheng_mima(mima_neirong):
            return JsonResponse({
                'zhuangtai_ma': 'mima_cuowu',
                'tishi_xinxi': '密码验证失败'
            })
        
        kanche_duixiang.zuijin_denglu = datetime.now()
        kanche_duixiang.save()
        
        qingqiu.session['kanche_bianhao'] = kanche_duixiang.kanche_bianhao
        qingqiu.session['kanche_mingcheng'] = kanche_duixiang.mingcheng_xianshi
        
        return JsonResponse({
            'zhuangtai_ma': 'denglu_chenggong',
            'tishi_xinxi': '登录成功',
            'tiaozhuan_dizhi': reverse('zhongxin_xianshi')
        })
        
    except Kanche.DoesNotExist:
        return JsonResponse({
            'zhuangtai_ma': 'yonghu_bucunzai',
            'tishi_xinxi': '用户档案不存在'
        })


def denglu_likakai(qingqiu):
    """登录离开处理"""
    qingqiu.session.flush()
    return redirect(reverse('denglu_xianshi'))


def denglu_yanzhengma(qingqiu):
    """登录验证码生成"""
    zijie_shuju, yanzhengma_wenzi = chuangjian_yanzhengma()
    qingqiu.session['yanzhengma_mima'] = yanzhengma_wenzi
    return HttpResponse(zijie_shuju, content_type='image/png')


@xuyao_kanche
def zhongxin_xianshi(qingqiu):
    """中心显示页面"""
    kanche = qingqiu.kanche
    
    tongji_shuju = {
        'kanche_shuliang': Kanche.objects.filter(huodong_zhuangtai=168).count(),
        'juese_shuliang': Juese.objects.filter(qiyong_zhuangtai=234).count(),
        'daohang_shuliang': Daohang.objects.filter(xianshi_zhuangtai=145).count(),
        'zuijin_caozuo': Caozuo.objects.all()[:10]
    }
    
    daohang_shuju = goujian_kanche_daohang(kanche)
    
    shangxiawen = {
        'kanche': kanche,
        'tongji_shuju': tongji_shuju,
        'daohang_shuju': daohang_shuju
    }
    
    return render(qingqiu, 'zhongxin/xianshi.html', shangxiawen)


def goujian_kanche_daohang(kanche):
    """构建勘察员导航树"""
    daohang_id_jh = set()
    for juese in kanche.juese_guanlian.filter(qiyong_zhuangtai=234):
        daohang_id_jh.update(
            juese.daohang_guanlian.filter(xianshi_zhuangtai=145).values_list('daohang_bianhao', flat=True)
        )
    
    daohang_list = Daohang.objects.filter(daohang_bianhao__in=daohang_id_jh).order_by('paixu_haoma')
    
    daohang_shu = []
    daohang_zidian = {dh.daohang_bianhao: dh for dh in daohang_list}
    
    for daohang in daohang_list:
        if not daohang.fuji_daohang:
            daohang_shu.append(goujian_daohang_jiedian(daohang, daohang_zidian))
    
    return daohang_shu


def goujian_daohang_jiedian(daohang, daohang_zidian):
    """构建导航节点"""
    jiedian = {
        'bianhao': daohang.daohang_bianhao,
        'bianma': daohang.daohang_bianma,
        'biaoti': daohang.daohang_biaoti,
        'leixing': daohang.leixing_xuanze,
        'luyou': daohang.luyou_dizhi,
        'tubiao': daohang.tubiao_yangshi,
        'zijiedian': []
    }
    
    for dh in daohang_zidian.values():
        if dh.fuji_daohang and dh.fuji_daohang.daohang_bianhao == daohang.daohang_bianhao:
            jiedian['zijiedian'].append(goujian_daohang_jiedian(dh, daohang_zidian))
    
    return jiedian


@xuyao_kanche
def kanche_liebiao(qingqiu):
    """勘察员列表页面"""
    return render(qingqiu, 'kanche/liebiao.html')


@xuyao_kanche
def kanche_shujuliu(qingqiu):
    """勘察员数据流"""
    yema_haoma = int(qingqiu.GET.get('page', 1))
    meiyet_shuliang = int(qingqiu.GET.get('limit', 10))
    sousuo_neirong = qingqiu.GET.get('search', '').strip()
    
    chaxun_tiaojian = Q()
    if sousuo_neirong:
        chaxun_tiaojian &= Q(denglu_biaoshi__icontains=sousuo_neirong) | Q(mingcheng_xianshi__icontains=sousuo_neirong)
    
    kanche_jh = Kanche.objects.filter(chaxun_tiaojian)
    zongshu = kanche_jh.count()
    
    kaishi_weizhi = (yema_haoma - 1) * meiyet_shuliang
    jieshu_weizhi = kaishi_weizhi + meiyet_shuliang
    kanche_jh = kanche_jh[kaishi_weizhi:jieshu_weizhi]
    
    shuju_list = []
    for kc in kanche_jh:
        juese_liebiao = [js.juese_mingcheng for js in kc.juese_guanlian.all()]
        shuju_list.append({
            'kanche_bianhao': kc.kanche_bianhao,
            'denglu_biaoshi': kc.denglu_biaoshi,
            'mingcheng_xianshi': kc.mingcheng_xianshi,
            'lianxi_dianhua': kc.lianxi_dianhua or '',
            'dianzi_youjian': kc.dianzi_youjian or '',
            'huodong_zhuangtai': kc.huodong_zhuangtai,
            'zhuangtai_wenzi': '活跃勘察' if kc.huodong_zhuangtai == 168 else '休眠封存',
            'juese_liebiao': ', '.join(juese_liebiao),
            'chuangjian_shijian': kc.chuangjian_shijian.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse({'code': 0, 'msg': '', 'count': zongshu, 'data': shuju_list})


@xuyao_kanche
@require_http_methods(["POST"])
def kanche_chuangjian(qingqiu):
    """勘察员创建"""
    try:
        denglu_biaoshi = qingqiu.POST.get('denglu_biaoshi', '').strip()
        mingcheng_xianshi = qingqiu.POST.get('mingcheng_xianshi', '').strip()
        mima_neirong = qingqiu.POST.get('mima_neirong', '').strip()
        lianxi_dianhua = qingqiu.POST.get('lianxi_dianhua', '').strip()
        dianzi_youjian = qingqiu.POST.get('dianzi_youjian', '').strip()
        juese_id_list = qingqiu.POST.getlist('juese_id_list[]')
        
        if not denglu_biaoshi or not mingcheng_xianshi or not mima_neirong:
            return JsonResponse({
                'zhuangtai_ma': 'shuju_buquan',
                'tishi_xinxi': '必填数据不完整'
            })
        
        if Kanche.objects.filter(denglu_biaoshi=denglu_biaoshi).exists():
            return JsonResponse({
                'zhuangtai_ma': 'biaoshi_chongfu',
                'tishi_xinxi': '登录标识已被使用'
            })
        
        kanche = Kanche.objects.create(
            denglu_biaoshi=denglu_biaoshi,
            mingcheng_xianshi=mingcheng_xianshi,
            lianxi_dianhua=lianxi_dianhua,
            dianzi_youjian=dianzi_youjian,
            huodong_zhuangtai=168
        )
        kanche.shezhi_mima(mima_neirong)
        kanche.save()
        
        if juese_id_list:
            juese_jh = Juese.objects.filter(juese_bianhao__in=juese_id_list)
            kanche.juese_guanlian.set(juese_jh)
        
        return JsonResponse({
            'zhuangtai_ma': 'chuangjian_chenggong',
            'tishi_xinxi': '勘察员创建成功'
        })
        
    except Exception as yichang:
        return JsonResponse({
            'zhuangtai_ma': 'chuangjian_shibai',
            'tishi_xinxi': f'创建失败: {str(yichang)}'
        })


@xuyao_kanche
@require_http_methods(["POST"])
def kanche_xiugai(qingqiu, kanche_bianhao):
    """勘察员修改"""
    try:
        kanche = get_object_or_404(Kanche, kanche_bianhao=kanche_bianhao)
        
        mingcheng_xianshi = qingqiu.POST.get('mingcheng_xianshi', '').strip()
        lianxi_dianhua = qingqiu.POST.get('lianxi_dianhua', '').strip()
        dianzi_youjian = qingqiu.POST.get('dianzi_youjian', '').strip()
        mima_neirong = qingqiu.POST.get('mima_neirong', '').strip()
        juese_id_list = qingqiu.POST.getlist('juese_id_list[]')
        huodong_zhuangtai = qingqiu.POST.get('huodong_zhuangtai', '168')
        
        kanche.mingcheng_xianshi = mingcheng_xianshi
        kanche.lianxi_dianhua = lianxi_dianhua
        kanche.dianzi_youjian = dianzi_youjian
        kanche.huodong_zhuangtai = int(huodong_zhuangtai)
        
        if mima_neirong:
            kanche.shezhi_mima(mima_neirong)
        
        kanche.save()
        
        if juese_id_list:
            juese_jh = Juese.objects.filter(juese_bianhao__in=juese_id_list)
            kanche.juese_guanlian.set(juese_jh)
        
        return JsonResponse({
            'zhuangtai_ma': 'xiugai_chenggong',
            'tishi_xinxi': '勘察员修改成功'
        })
        
    except Exception as yichang:
        return JsonResponse({
            'zhuangtai_ma': 'xiugai_shibai',
            'tishi_xinxi': f'修改失败: {str(yichang)}'
        })


@xuyao_kanche
@require_http_methods(["POST"])
def kanche_shanchu(qingqiu, kanche_bianhao):
    """勘察员删除"""
    try:
        kanche = get_object_or_404(Kanche, kanche_bianhao=kanche_bianhao)
        
        if kanche.kanche_bianhao == qingqiu.kanche.kanche_bianhao:
            return JsonResponse({
                'zhuangtai_ma': 'buneng_shanchu_ziji',
                'tishi_xinxi': '不能删除自己的账户'
            })
        
        kanche.delete()
        return JsonResponse({
            'zhuangtai_ma': 'shanchu_chenggong',
            'tishi_xinxi': '勘察员删除成功'
        })
        
    except Exception as yichang:
        return JsonResponse({
            'zhuangtai_ma': 'shanchu_shibai',
            'tishi_xinxi': f'删除失败: {str(yichang)}'
        })


@xuyao_kanche
def juese_liebiao(qingqiu):
    """角色列表页面"""
    return render(qingqiu, 'juese/liebiao.html')


@xuyao_kanche
def juese_shujuliu(qingqiu):
    """角色数据流"""
    yema_haoma = int(qingqiu.GET.get('page', 1))
    meiyet_shuliang = int(qingqiu.GET.get('limit', 10))
    sousuo_neirong = qingqiu.GET.get('search', '').strip()
    
    chaxun_tiaojian = Q()
    if sousuo_neirong:
        chaxun_tiaojian &= Q(juese_daima__icontains=sousuo_neirong) | Q(juese_mingcheng__icontains=sousuo_neirong)
    
    juese_jh = Juese.objects.filter(chaxun_tiaojian)
    zongshu = juese_jh.count()
    
    kaishi_weizhi = (yema_haoma - 1) * meiyet_shuliang
    jieshu_weizhi = kaishi_weizhi + meiyet_shuliang
    juese_jh = juese_jh[kaishi_weizhi:jieshu_weizhi]
    
    shuju_list = []
    for js in juese_jh:
        daohang_liebiao = [dh.daohang_biaoti for dh in js.daohang_guanlian.all()]
        shuju_list.append({
            'juese_bianhao': js.juese_bianhao,
            'juese_daima': js.juese_daima,
            'juese_mingcheng': js.juese_mingcheng,
            'dengji_shuzhi': js.dengji_shuzhi,
            'qiyong_zhuangtai': js.qiyong_zhuangtai,
            'zhuangtai_wenzi': '启用状态' if js.qiyong_zhuangtai == 234 else '禁用状态',
            'daohang_liebiao': ', '.join(daohang_liebiao),
            'chuangjian_shijian': js.chuangjian_shijian.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse({'code': 0, 'msg': '', 'count': zongshu, 'data': shuju_list})


@xuyao_kanche
@require_http_methods(["POST"])
def juese_chuangjian(qingqiu):
    """角色创建"""
    try:
        juese_daima = qingqiu.POST.get('juese_daima', '').strip()
        juese_mingcheng = qingqiu.POST.get('juese_mingcheng', '').strip()
        dengji_shuzhi = qingqiu.POST.get('dengji_shuzhi', '888')
        daohang_id_list = qingqiu.POST.getlist('daohang_id_list[]')
        
        if not juese_daima or not juese_mingcheng:
            return JsonResponse({
                'zhuangtai_ma': 'shuju_buquan',
                'tishi_xinxi': '必填数据不完整'
            })
        
        if Juese.objects.filter(juese_daima=juese_daima).exists():
            return JsonResponse({
                'zhuangtai_ma': 'daima_chongfu',
                'tishi_xinxi': '角色代码已存在'
            })
        
        juese = Juese.objects.create(
            juese_daima=juese_daima,
            juese_mingcheng=juese_mingcheng,
            dengji_shuzhi=int(dengji_shuzhi),
            qiyong_zhuangtai=234
        )
        
        if daohang_id_list:
            daohang_jh = Daohang.objects.filter(daohang_bianhao__in=daohang_id_list)
            juese.daohang_guanlian.set(daohang_jh)
        
        return JsonResponse({
            'zhuangtai_ma': 'chuangjian_chenggong',
            'tishi_xinxi': '角色创建成功'
        })
        
    except Exception as yichang:
        return JsonResponse({
            'zhuangtai_ma': 'chuangjian_shibai',
            'tishi_xinxi': f'创建失败: {str(yichang)}'
        })


@xuyao_kanche
@require_http_methods(["POST"])
def juese_xiugai(qingqiu, juese_bianhao):
    """角色修改"""
    try:
        juese = get_object_or_404(Juese, juese_bianhao=juese_bianhao)
        
        juese_mingcheng = qingqiu.POST.get('juese_mingcheng', '').strip()
        dengji_shuzhi = qingqiu.POST.get('dengji_shuzhi', '888')
        daohang_id_list = qingqiu.POST.getlist('daohang_id_list[]')
        qiyong_zhuangtai = qingqiu.POST.get('qiyong_zhuangtai', '234')
        
        juese.juese_mingcheng = juese_mingcheng
        juese.dengji_shuzhi = int(dengji_shuzhi)
        juese.qiyong_zhuangtai = int(qiyong_zhuangtai)
        juese.save()
        
        if daohang_id_list:
            daohang_jh = Daohang.objects.filter(daohang_bianhao__in=daohang_id_list)
            juese.daohang_guanlian.set(daohang_jh)
        
        return JsonResponse({
            'zhuangtai_ma': 'xiugai_chenggong',
            'tishi_xinxi': '角色修改成功'
        })
        
    except Exception as yichang:
        return JsonResponse({
            'zhuangtai_ma': 'xiugai_shibai',
            'tishi_xinxi': f'修改失败: {str(yichang)}'
        })


@xuyao_kanche
@require_http_methods(["POST"])
def juese_shanchu(qingqiu, juese_bianhao):
    """角色删除"""
    try:
        juese = get_object_or_404(Juese, juese_bianhao=juese_bianhao)
        juese.delete()
        return JsonResponse({
            'zhuangtai_ma': 'shanchu_chenggong',
            'tishi_xinxi': '角色删除成功'
        })
        
    except Exception as yichang:
        return JsonResponse({
            'zhuangtai_ma': 'shanchu_shibai',
            'tishi_xinxi': f'删除失败: {str(yichang)}'
        })


@xuyao_kanche
def daohang_liebiao(qingqiu):
    """导航列表页面"""
    return render(qingqiu, 'daohang/liebiao.html')


@xuyao_kanche
def daohang_shujuliu(qingqiu):
    """导航数据流（树形）"""
    daohang_jh = Daohang.objects.all().order_by('paixu_haoma')
    
    shuju_list = []
    daohang_zidian = {dh.daohang_bianhao: dh for dh in daohang_jh}
    
    for daohang in daohang_jh:
        if not daohang.fuji_daohang:
            shuju_list.append(goujian_daohang_shuju(daohang, daohang_zidian))
    
    return JsonResponse({'code': 0, 'msg': '', 'data': shuju_list})


def goujian_daohang_shuju(daohang, daohang_zidian):
    """构建导航数据"""
    jiedian = {
        'daohang_bianhao': daohang.daohang_bianhao,
        'daohang_bianma': daohang.daohang_bianma,
        'daohang_biaoti': daohang.daohang_biaoti,
        'leixing_xuanze': daohang.leixing_xuanze,
        'fuji_bianhao': daohang.fuji_daohang.daohang_bianhao if daohang.fuji_daohang else None,
        'luyou_dizhi': daohang.luyou_dizhi or '',
        'tubiao_yangshi': daohang.tubiao_yangshi or '',
        'paixu_haoma': daohang.paixu_haoma,
        'xianshi_zhuangtai': daohang.xianshi_zhuangtai,
        'zhuangtai_wenzi': '显示状态' if daohang.xianshi_zhuangtai == 145 else '隐藏状态',
        'chuangjian_shijian': daohang.chuangjian_shijian.strftime('%Y-%m-%d %H:%M:%S'),
        'children': []
    }
    
    for dh in daohang_zidian.values():
        if dh.fuji_daohang and dh.fuji_daohang.daohang_bianhao == daohang.daohang_bianhao:
            jiedian['children'].append(goujian_daohang_shuju(dh, daohang_zidian))
    
    return jiedian


@xuyao_kanche
@require_http_methods(["POST"])
def daohang_chuangjian(qingqiu):
    """导航创建"""
    try:
        daohang_bianma = qingqiu.POST.get('daohang_bianma', '').strip()
        daohang_biaoti = qingqiu.POST.get('daohang_biaoti', '').strip()
        leixing_xuanze = qingqiu.POST.get('leixing_xuanze', 'caidian')
        fuji_bianhao = qingqiu.POST.get('fuji_bianhao', '')
        luyou_dizhi = qingqiu.POST.get('luyou_dizhi', '').strip()
        tubiao_yangshi = qingqiu.POST.get('tubiao_yangshi', '').strip()
        paixu_haoma = qingqiu.POST.get('paixu_haoma', '0')
        
        if not daohang_bianma or not daohang_biaoti:
            return JsonResponse({
                'zhuangtai_ma': 'shuju_buquan',
                'tishi_xinxi': '必填数据不完整'
            })
        
        if Daohang.objects.filter(daohang_bianma=daohang_bianma).exists():
            return JsonResponse({
                'zhuangtai_ma': 'bianma_chongfu',
                'tishi_xinxi': '导航编码已存在'
            })
        
        daohang = Daohang.objects.create(
            daohang_bianma=daohang_bianma,
            daohang_biaoti=daohang_biaoti,
            leixing_xuanze=leixing_xuanze,
            luyou_dizhi=luyou_dizhi,
            tubiao_yangshi=tubiao_yangshi,
            paixu_haoma=int(paixu_haoma),
            xianshi_zhuangtai=145
        )
        
        if fuji_bianhao:
            fuji = Daohang.objects.get(daohang_bianhao=int(fuji_bianhao))
            daohang.fuji_daohang = fuji
            daohang.save()
        
        return JsonResponse({
            'zhuangtai_ma': 'chuangjian_chenggong',
            'tishi_xinxi': '导航创建成功'
        })
        
    except Exception as yichang:
        return JsonResponse({
            'zhuangtai_ma': 'chuangjian_shibai',
            'tishi_xinxi': f'创建失败: {str(yichang)}'
        })


@xuyao_kanche
@require_http_methods(["POST"])
def daohang_xiugai(qingqiu, daohang_bianhao):
    """导航修改"""
    try:
        daohang = get_object_or_404(Daohang, daohang_bianhao=daohang_bianhao)
        
        daohang_biaoti = qingqiu.POST.get('daohang_biaoti', '').strip()
        leixing_xuanze = qingqiu.POST.get('leixing_xuanze', 'caidian')
        fuji_bianhao = qingqiu.POST.get('fuji_bianhao', '')
        luyou_dizhi = qingqiu.POST.get('luyou_dizhi', '').strip()
        tubiao_yangshi = qingqiu.POST.get('tubiao_yangshi', '').strip()
        paixu_haoma = qingqiu.POST.get('paixu_haoma', '0')
        xianshi_zhuangtai = qingqiu.POST.get('xianshi_zhuangtai', '145')
        
        daohang.daohang_biaoti = daohang_biaoti
        daohang.leixing_xuanze = leixing_xuanze
        daohang.luyou_dizhi = luyou_dizhi
        daohang.tubiao_yangshi = tubiao_yangshi
        daohang.paixu_haoma = int(paixu_haoma)
        daohang.xianshi_zhuangtai = int(xianshi_zhuangtai)
        
        if fuji_bianhao:
            fuji = Daohang.objects.get(daohang_bianhao=int(fuji_bianhao))
            daohang.fuji_daohang = fuji
        else:
            daohang.fuji_daohang = None
        
        daohang.save()
        
        return JsonResponse({
            'zhuangtai_ma': 'xiugai_chenggong',
            'tishi_xinxi': '导航修改成功'
        })
        
    except Exception as yichang:
        return JsonResponse({
            'zhuangtai_ma': 'xiugai_shibai',
            'tishi_xinxi': f'修改失败: {str(yichang)}'
        })


@xuyao_kanche
@require_http_methods(["POST"])
def daohang_shanchu(qingqiu, daohang_bianhao):
    """导航删除"""
    try:
        daohang = get_object_or_404(Daohang, daohang_bianhao=daohang_bianhao)
        
        if daohang.ziji_daohang.exists():
            return JsonResponse({
                'zhuangtai_ma': 'you_zijiedian',
                'tishi_xinxi': '存在子节点，无法删除'
            })
        
        daohang.delete()
        return JsonResponse({
            'zhuangtai_ma': 'shanchu_chenggong',
            'tishi_xinxi': '导航删除成功'
        })
        
    except Exception as yichang:
        return JsonResponse({
            'zhuangtai_ma': 'shanchu_shibai',
            'tishi_xinxi': f'删除失败: {str(yichang)}'
        })


@xuyao_kanche
def huoqu_juese_mulu(qingqiu):
    """获取角色目录"""
    juese_jh = Juese.objects.filter(qiyong_zhuangtai=234).order_by('dengji_shuzhi')
    mulu = [{
        'bianhao': js.juese_bianhao,
        'mingcheng': js.juese_mingcheng,
        'daima': js.juese_daima
    } for js in juese_jh]
    return JsonResponse({'zhuangtai_ma': 'chenggong', 'mulu': mulu})


@xuyao_kanche
def huoqu_daohang_mulu(qingqiu):
    """获取导航目录"""
    daohang_jh = Daohang.objects.filter(xianshi_zhuangtai=145).order_by('paixu_haoma')
    mulu = []
    for dh in daohang_jh:
        mulu.append({
            'bianhao': dh.daohang_bianhao,
            'biaoti': dh.daohang_biaoti,
            'bianma': dh.daohang_bianma,
            'fuji_bianhao': dh.fuji_daohang.daohang_bianhao if dh.fuji_daohang else None
        })
    return JsonResponse({'zhuangtai_ma': 'chenggong', 'mulu': mulu})
