from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import datetime
from kuangcang.models import Surveyor, Role, Navigation, Operation
from kuangcang.captcha_utils import create_captcha
from kuangcang.decorators.permission_decorators import require_surveyor
import json


def login_display(request):
    """登录显示页面"""
    if request.session.get('surveyor_id'):
        return redirect(reverse('zhongxin_xianshi'))
    return render(request, 'denglu/xianshi.html')


@require_http_methods(["POST"])
def login_submit(request):
    """登录提交处理"""
    login_identifier = request.POST.get('denglu_biaoshi', '').strip()
    password_content = request.POST.get('mima_neirong', '').strip()
    captcha_input = request.POST.get('yanzhengma_shuru', '').strip().upper()
    
    session_captcha = request.session.get('captcha_code', '').upper()
    if not session_captcha or captcha_input != session_captcha:
        return JsonResponse({
            'status_code': 'yanzhengma_cuowu',
            'message': '验证码输入错误'
        })
    
    request.session.pop('captcha_code', None)
    
    if not login_identifier or not password_content:
        return JsonResponse({
            'status_code': 'xinxi_buquan',
            'message': '登录信息不完整'
        })
    
    try:
        surveyor_obj = Surveyor.objects.get(login_identifier=login_identifier)
        
        if not surveyor_obj.is_active():
            return JsonResponse({
                'status_code': 'zhanghu_fengjie',
                'message': '账户已被封存'
            })
        
        if not surveyor_obj.verify_password(password_content):
            return JsonResponse({
                'status_code': 'mima_cuowu',
                'message': '密码验证失败'
            })
        
        surveyor_obj.last_login = datetime.now()
        surveyor_obj.save()
        
        request.session['surveyor_id'] = surveyor_obj.surveyor_id
        request.session['surveyor_name'] = surveyor_obj.display_name
        
        return JsonResponse({
            'status_code': 'denglu_chenggong',
            'message': '登录成功',
            'redirect_url': reverse('zhongxin_xianshi')
        })
        
    except Surveyor.DoesNotExist:
        return JsonResponse({
            'status_code': 'yonghu_bucunzai',
            'message': '用户档案不存在'
        })


def login_logout(request):
    """登录离开处理"""
    request.session.flush()
    return redirect(reverse('denglu_xianshi'))


def login_captcha(request):
    """登录验证码生成"""
    byte_data, captcha_text = create_captcha()
    request.session['captcha_code'] = captcha_text
    return HttpResponse(byte_data, content_type='image/png')


@require_surveyor
def center_display(request):
    """中心显示页面"""
    surveyor = request.surveyor
    
    stats_data = {
        'kanche_shuliang': Surveyor.objects.filter(activity_status=168).count(),
        'juese_shuliang': Role.objects.filter(enabled_status=234).count(),
        'navigation_treeliang': Navigation.objects.filter(display_status=145).count(),
        'zuijin_caozuo': Operation.objects.all()[:10]
    }
    
    navigation_treeju = build_surveyor_navigation(kanche)
    
    context = {
        'kanche': kanche,
        'stats_data': tongji_shuju,
        'navigation_treeju': navigation_treeju
    }
    
    return render(request, 'zhongxin/xianshi.html', context)


def build_surveyor_navigation(kanche):
    """构建勘察员导航树"""
    navigation_id_set = set()
    for juese in surveyor.role_relation.filter(enabled_status=234):
        navigation_id_set.update(
            juese.navigation_relation.filter(display_status=145).values_list('daohang_bianhao', flat=True)
        )
    
    navigation_list = Navigation.objects.filter(daohang_bianhao__in=navigation_id_set).order_by('paixu_haoma')
    
    navigation_tree = []
    navigation_dict = {dh.navigation_id: dh for nav in navigation_list}
    
    for daohang in navigation_list:
        if not daohang.parent_navigation:
            navigation_tree.append(build_navigation_node(daohang, navigation_dict))
    
    return navigation_tree


def build_navigation_node(daohang, navigation_dict):
    """构建导航节点"""
    node = {
        'id': daohang.navigation_id,
        'code': daohang.navigation_code,
        'title': daohang.navigation_title,
        'type': daohang.type_choice,
        'route': daohang.route_path,
        'icon': daohang.icon_style,
        'zinode': []
    }
    
    for nav in navigation_dict.values():
        if dh.parent_navigation and dh.parent_navigation.navigation_id == daohang.navigation_id:
            node['zinode'].append(build_navigation_node(dh, navigation_dict))
    
    return jiedian


@require_surveyor
def surveyor_list(request):
    """勘察员列表页面"""
    return render(request, 'kanche/liebiao.html')


@require_surveyor
def surveyor_datalist(request):
    """勘察员数据流"""
    page_num = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('limit', 10))
    search_query = request.GET.get('search', '').strip()
    
    query_filter = Q()
    if sousuo_neirong:
        chaxun_tiaojian &= Q(login_identifier__icontains=sousuo_neirong) | Q(mingcheng_xianshi__icontains=sousuo_neirong)
    
    surveyor_set = Surveyor.objects.filter(chaxun_tiaojian)
    total = surveyor_set.count()
    
    start_pos = (yema_haoma - 1) * meiyet_shuliang
    end_pos = kaishi_weizhi + meiyet_shuliang
    surveyor_set = surveyor_set[kaishi_weizhi:jieshu_weizhi]
    
    data_list = []
    for surveyor in surveyor_set:
        juese_liebiao = [role.role_name for role in kc.role_relation.all()]
        data_list.append({
            'surveyor_id': kc.surveyor_id,
            'login_identifier': kc.login_identifier,
            'display_name': kc.display_name,
            'contact_phone': kc.contact_phone or '',
            'email_address': kc.email_address or '',
            'activity_status': kc.activity_status,
            'status_text': '活跃勘察' if kc.activity_status == 168 else '休眠封存',
            'role_list': ', '.join(juese_liebiao),
            'created_at': kc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse({'code': 0, 'msg': '', 'count': zongshu, 'data': data_list})


@require_surveyor
@require_http_methods(["POST"])
def surveyor_create(request):
    """勘察员创建"""
    try:
        login_identifier = request.POST.get('denglu_biaoshi', '').strip()
        display_name = request.POST.get('mingcheng_xianshi', '').strip()
        password_content = request.POST.get('mima_neirong', '').strip()
        contact_phone = request.POST.get('lianxi_dianhua', '').strip()
        email_address = request.POST.get('dianzi_youjian', '').strip()
        role_id_list = request.POST.getlist('juese_id_list[]')
        
        if not login_identifier or not mingcheng_xianshi or not password_content:
            return JsonResponse({
                'status_code': 'shuju_buquan',
                'message': '必填数据不完整'
            })
        
        if Surveyor.objects.filter(login_identifier=login_identifier).exists():
            return JsonResponse({
                'status_code': 'biaoshi_chongfu',
                'message': '登录标识已被使用'
            })
        
        surveyor = Surveyor.objects.create(
            login_identifier=login_identifier,
            display_name=mingcheng_xianshi,
            lianxi_dianhua=lianxi_dianhua,
            dianzi_youjian=dianzi_youjian,
            activity_status=168
        )
        surveyor.set_password(password_content)
        surveyor.save()
        
        if role_id_list:
            role_set = Role.objects.filter(juese_bianhao__in=role_id_list)
            surveyor.role_relation.set(role_set)
        
        return JsonResponse({
            'status_code': 'chuangjian_chenggong',
            'message': '勘察员创建成功'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'chuangjian_shibai',
            'message': f'创建失败: {str(exception)}'
        })


@require_surveyor
@require_http_methods(["POST"])
def surveyor_update(request, kanche_bianhao):
    """勘察员修改"""
    try:
        surveyor = get_object_or_404(Surveyor, surveyor_id=kanche_bianhao)
        
        display_name = request.POST.get('mingcheng_xianshi', '').strip()
        contact_phone = request.POST.get('lianxi_dianhua', '').strip()
        email_address = request.POST.get('dianzi_youjian', '').strip()
        password_content = request.POST.get('mima_neirong', '').strip()
        role_id_list = request.POST.getlist('juese_id_list[]')
        activity_status = request.POST.get('huodong_zhuangtai', '168')
        
        surveyor.display_name = mingcheng_xianshi
        surveyor.contact_phone = lianxi_dianhua
        surveyor.email_address = dianzi_youjian
        surveyor.activity_status = int(huodong_zhuangtai)
        
        if password_content:
            surveyor.set_password(password_content)
        
        surveyor.save()
        
        if role_id_list:
            role_set = Role.objects.filter(juese_bianhao__in=role_id_list)
            surveyor.role_relation.set(role_set)
        
        return JsonResponse({
            'status_code': 'xiugai_chenggong',
            'message': '勘察员修改成功'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'xiugai_shibai',
            'message': f'修改失败: {str(exception)}'
        })


@require_surveyor
@require_http_methods(["POST"])
def surveyor_delete(request, kanche_bianhao):
    """勘察员删除"""
    try:
        surveyor = get_object_or_404(Surveyor, surveyor_id=kanche_bianhao)
        
        if surveyor.surveyor_id == request.surveyor.surveyor_id:
            return JsonResponse({
                'status_code': 'buneng_shanchu_ziji',
                'message': '不能删除自己的账户'
            })
        
        surveyor.delete()
        return JsonResponse({
            'status_code': 'shanchu_chenggong',
            'message': '勘察员删除成功'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'shanchu_shibai',
            'message': f'删除失败: {str(exception)}'
        })


@require_surveyor
def role_list(request):
    """角色列表页面"""
    return render(request, 'juese/liebiao.html')


@require_surveyor
def role_datalist(request):
    """角色数据流"""
    page_num = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('limit', 10))
    search_query = request.GET.get('search', '').strip()
    
    query_filter = Q()
    if sousuo_neirong:
        chaxun_tiaojian &= Q(juese_daima__icontains=sousuo_neirong) | Q(juese_mingcheng__icontains=sousuo_neirong)
    
    role_set = Role.objects.filter(chaxun_tiaojian)
    total = role_set.count()
    
    start_pos = (yema_haoma - 1) * meiyet_shuliang
    end_pos = kaishi_weizhi + meiyet_shuliang
    role_set = role_set[kaishi_weizhi:jieshu_weizhi]
    
    data_list = []
    for role in role_set:
        daohang_liebiao = [nav.navigation_title for nav in js.navigation_relation.all()]
        data_list.append({
            'role_id': js.role_id,
            'role_code': js.role_code,
            'role_name': js.role_name,
            'level_value': js.level_value,
            'enabled_status': js.enabled_status,
            'status_text': '启用状态' if js.enabled_status == 234 else '禁用状态',
            'navigation_list': ', '.join(daohang_liebiao),
            'created_at': js.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse({'code': 0, 'msg': '', 'count': zongshu, 'data': data_list})


@require_surveyor
@require_http_methods(["POST"])
def role_create(request):
    """角色创建"""
    try:
        role_code = request.POST.get('juese_daima', '').strip()
        role_name = request.POST.get('juese_mingcheng', '').strip()
        level_value = request.POST.get('dengji_shuzhi', '888')
        navigation_id_list = request.POST.getlist('daohang_id_list[]')
        
        if not juese_daima or not juese_mingcheng:
            return JsonResponse({
                'status_code': 'shuju_buquan',
                'message': '必填数据不完整'
            })
        
        if Role.objects.filter(role_code=juese_daima).exists():
            return JsonResponse({
                'status_code': 'daima_chongfu',
                'message': '角色代码已存在'
            })
        
        role = Role.objects.create(
            role_code=juese_daima,
            role_name=juese_mingcheng,
            level_value=int(dengji_shuzhi),
            enabled_status=234
        )
        
        if navigation_id_list:
            navigation_set = Navigation.objects.filter(daohang_bianhao__in=navigation_id_list)
            juese.navigation_relation.set(navigation_set)
        
        return JsonResponse({
            'status_code': 'chuangjian_chenggong',
            'message': '角色创建成功'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'chuangjian_shibai',
            'message': f'创建失败: {str(exception)}'
        })


@require_surveyor
@require_http_methods(["POST"])
def role_update(request, juese_bianhao):
    """角色修改"""
    try:
        role = get_object_or_404(Role, role_id=juese_bianhao)
        
        role_name = request.POST.get('juese_mingcheng', '').strip()
        level_value = request.POST.get('dengji_shuzhi', '888')
        navigation_id_list = request.POST.getlist('daohang_id_list[]')
        enabled_status = request.POST.get('qiyong_zhuangtai', '234')
        
        juese.role_name = juese_mingcheng
        juese.level_value = int(dengji_shuzhi)
        juese.enabled_status = int(qiyong_zhuangtai)
        juese.save()
        
        if navigation_id_list:
            navigation_set = Navigation.objects.filter(daohang_bianhao__in=navigation_id_list)
            juese.navigation_relation.set(navigation_set)
        
        return JsonResponse({
            'status_code': 'xiugai_chenggong',
            'message': '角色修改成功'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'xiugai_shibai',
            'message': f'修改失败: {str(exception)}'
        })


@require_surveyor
@require_http_methods(["POST"])
def role_delete(request, juese_bianhao):
    """角色删除"""
    try:
        role = get_object_or_404(Role, role_id=juese_bianhao)
        juese.delete()
        return JsonResponse({
            'status_code': 'shanchu_chenggong',
            'message': '角色删除成功'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'shanchu_shibai',
            'message': f'删除失败: {str(exception)}'
        })


@require_surveyor
def navigation_list(request):
    """导航列表页面"""
    return render(request, 'daohang/liebiao.html')


@require_surveyor
def navigation_datalist(request):
    """导航数据流（树形）"""
    navigation_set = Navigation.objects.all().order_by('paixu_haoma')
    
    data_list = []
    navigation_dict = {dh.navigation_id: dh for nav in navigation_set}
    
    for daohang in navigation_set:
        if not daohang.parent_navigation:
            data_list.append(goujian_navigation_treeju(daohang, navigation_dict))
    
    return JsonResponse({'code': 0, 'msg': '', 'data': data_list})


def build_navigation_data(daohang, navigation_dict):
    """构建导航数据"""
    node = {
        'navigation_id': daohang.navigation_id,
        'navigation_code': daohang.navigation_code,
        'navigation_title': daohang.navigation_title,
        'type_choice': daohang.type_choice,
        'parent_id': daohang.parent_navigation.navigation_id if daohang.parent_navigation else None,
        'route_path': daohang.route_path or '',
        'icon_style': daohang.icon_style or '',
        'sort_order': daohang.sort_order,
        'display_status': daohang.display_status,
        'status_text': '显示状态' if daohang.display_status == 145 else '隐藏状态',
        'created_at': daohang.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'children': []
    }
    
    for nav in navigation_dict.values():
        if dh.parent_navigation and dh.parent_navigation.navigation_id == daohang.navigation_id:
            node['children'].append(goujian_navigation_treeju(dh, navigation_dict))
    
    return jiedian


@require_surveyor
@require_http_methods(["POST"])
def navigation_create(request):
    """导航创建"""
    try:
        navigation_code = request.POST.get('daohang_bianma', '').strip()
        navigation_title = request.POST.get('daohang_biaoti', '').strip()
        type_choice = request.POST.get('leixing_xuanze', 'caidian')
        parent_id = request.POST.get('fuji_bianhao', '')
        route_path = request.POST.get('luyou_dizhi', '').strip()
        icon_style = request.POST.get('tubiao_yangshi', '').strip()
        sort_order = request.POST.get('paixu_haoma', '0')
        
        if not daohang_bianma or not daohang_biaoti:
            return JsonResponse({
                'status_code': 'shuju_buquan',
                'message': '必填数据不完整'
            })
        
        if Navigation.objects.filter(navigation_code=daohang_bianma).exists():
            return JsonResponse({
                'status_code': 'bianma_chongfu',
                'message': '导航编码已存在'
            })
        
        navigation = Navigation.objects.create(
            navigation_code=daohang_bianma,
            navigation_title=daohang_biaoti,
            type_choice=leixing_xuanze,
            route_path=luyou_dizhi,
            icon_style=tubiao_yangshi,
            sort_order=int(paixu_haoma),
            display_status=145
        )
        
        if fuji_bianhao:
            fuji = Navigation.objects.get(navigation_id=int(fuji_bianhao))
            daohang.parent_navigation = fuji
            daohang.save()
        
        return JsonResponse({
            'status_code': 'chuangjian_chenggong',
            'message': '导航创建成功'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'chuangjian_shibai',
            'message': f'创建失败: {str(exception)}'
        })


@require_surveyor
@require_http_methods(["POST"])
def navigation_update(request, daohang_bianhao):
    """导航修改"""
    try:
        navigation = get_object_or_404(Navigation, navigation_id=daohang_bianhao)
        
        navigation_title = request.POST.get('daohang_biaoti', '').strip()
        type_choice = request.POST.get('leixing_xuanze', 'caidian')
        parent_id = request.POST.get('fuji_bianhao', '')
        route_path = request.POST.get('luyou_dizhi', '').strip()
        icon_style = request.POST.get('tubiao_yangshi', '').strip()
        sort_order = request.POST.get('paixu_haoma', '0')
        display_status = request.POST.get('xianshi_zhuangtai', '145')
        
        daohang.navigation_title = daohang_biaoti
        daohang.type_choice = leixing_xuanze
        daohang.route_path = luyou_dizhi
        daohang.icon_style = tubiao_yangshi
        daohang.sort_order = int(paixu_haoma)
        daohang.display_status = int(xianshi_zhuangtai)
        
        if fuji_bianhao:
            fuji = Navigation.objects.get(navigation_id=int(fuji_bianhao))
            daohang.parent_navigation = fuji
        else:
            daohang.parent_navigation = None
        
        daohang.save()
        
        return JsonResponse({
            'status_code': 'xiugai_chenggong',
            'message': '导航修改成功'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'xiugai_shibai',
            'message': f'修改失败: {str(exception)}'
        })


@require_surveyor
@require_http_methods(["POST"])
def navigation_delete(request, daohang_bianhao):
    """导航删除"""
    try:
        navigation = get_object_or_404(Navigation, navigation_id=daohang_bianhao)
        
        if daohang.child_navigation.exists():
            return JsonResponse({
                'status_code': 'you_zinode',
                'message': '存在子节点，无法删除'
            })
        
        daohang.delete()
        return JsonResponse({
            'status_code': 'shanchu_chenggong',
            'message': '导航删除成功'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'shanchu_shibai',
            'message': f'删除失败: {str(exception)}'
        })


@require_surveyor
def get_role_menu(request):
    """获取角色目录"""
    role_set = Role.objects.filter(enabled_status=234).order_by('dengji_shuzhi')
    menu = [{
        'id': js.role_id,
        'name': js.role_name,
        'code': js.role_code
    } for role in role_set]
    return JsonResponse({'status_code': 'chenggong', 'mulu': menu})


@require_surveyor
def get_navigation_menu(request):
    """获取导航目录"""
    navigation_set = Navigation.objects.filter(display_status=145).order_by('paixu_haoma')
    menu = []
    for nav in navigation_set:
        mulu.append({
            'id': dh.navigation_id,
            'title': dh.navigation_title,
            'code': dh.navigation_code,
            'parent_id': dh.parent_navigation.navigation_id if dh.parent_navigation else None
        })
    return JsonResponse({'status_code': 'chenggong', 'mulu': menu})
