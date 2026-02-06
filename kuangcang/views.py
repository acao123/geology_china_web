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
    """Login display page"""
    if request.session.get('surveyor_id'):
        return redirect(reverse('center_display'))
    return render(request, 'login/display.html')


@require_http_methods(["POST"])
def login_submit(request):
    """Login submission handler"""
    login_identifier = request.POST.get('login_identifier', '').strip()
    password_content = request.POST.get('password', '').strip()
    captcha_input = request.POST.get('captcha', '').strip().upper()
    
    session_captcha = request.session.get('captcha_code', '').upper()
    if not session_captcha or captcha_input != session_captcha:
        return JsonResponse({
            'status_code': 'captcha_error',
            'message': 'Captcha verification failed'
        })
    
    request.session.pop('captcha_code', None)
    
    if not login_identifier or not password_content:
        return JsonResponse({
            'status_code': 'incomplete_info',
            'message': 'Login information incomplete'
        })
    
    try:
        surveyor_obj = Surveyor.objects.get(login_identifier=login_identifier)
        
        if not surveyor_obj.is_active():
            return JsonResponse({
                'status_code': 'account_archived',
                'message': 'Account has been archived'
            })
        
        if not surveyor_obj.verify_password(password_content):
            return JsonResponse({
                'status_code': 'password_error',
                'message': 'Password verification failed'
            })
        
        surveyor_obj.last_login = datetime.now()
        surveyor_obj.save()
        
        request.session['surveyor_id'] = surveyor_obj.surveyor_id
        request.session['surveyor_name'] = surveyor_obj.display_name
        
        return JsonResponse({
            'status_code': 'login_success',
            'message': 'Login successful',
            'redirect_url': reverse('center_display')
        })
        
    except Surveyor.DoesNotExist:
        return JsonResponse({
            'status_code': 'user_not_found',
            'message': 'User profile does not exist'
        })


def login_logout(request):
    """Logout handler"""
    request.session.flush()
    return redirect(reverse('login_display'))


def login_captcha(request):
    """Login captcha generation"""
    byte_data, captcha_text = create_captcha()
    request.session['captcha_code'] = captcha_text
    return HttpResponse(byte_data, content_type='image/png')


@require_surveyor
def center_display(request):
    """Center display page"""
    surveyor = request.surveyor
    
    stats_data = {
        'surveyor_count': Surveyor.objects.filter(activity_status=168).count(),
        'role_count': Role.objects.filter(enabled_status=234).count(),
        'navigation_count': Navigation.objects.filter(display_status=145).count(),
        'recent_operations': Operation.objects.all()[:10]
    }
    
    navigation_tree = build_surveyor_navigation(surveyor)
    
    context = {
        'surveyor': surveyor,
        'stats_data': stats_data,
        'navigation_tree': navigation_tree
    }
    
    return render(request, 'center/display.html', context)


def build_surveyor_navigation(surveyor):
    """Build surveyor navigation tree"""
    navigation_id_set = set()
    for role in surveyor.role_relation.filter(enabled_status=234):
        navigation_id_set.update(
            role.navigation_relation.filter(display_status=145).values_list('navigation_id', flat=True)
        )
    
    navigation_list = Navigation.objects.filter(navigation_id__in=navigation_id_set).order_by('sort_order')
    
    navigation_tree = []
    navigation_dict = {nav.navigation_id: nav for nav in navigation_list}
    
    for nav in navigation_list:
        if not nav.parent_navigation:
            navigation_tree.append(build_navigation_node(nav, navigation_dict))
    
    return navigation_tree


def build_navigation_node(nav, navigation_dict):
    """Build navigation node"""
    node = {
        'id': nav.navigation_id,
        'code': nav.navigation_code,
        'title': nav.navigation_title,
        'type': nav.type_choice,
        'route': nav.route_path,
        'icon': nav.icon_style,
        'children': []
    }
    
    for child in navigation_dict.values():
        if child.parent_navigation and child.parent_navigation.navigation_id == nav.navigation_id:
            node['children'].append(build_navigation_node(child, navigation_dict))
    
    return node


@require_surveyor
def surveyor_list(request):
    """Surveyor list page"""
    return render(request, 'surveyor/list.html')


@require_surveyor
def surveyor_datalist(request):
    """Surveyor data list"""
    page_num = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('limit', 10))
    search_query = request.GET.get('search', '').strip()
    
    query_filter = Q()
    if search_query:
        query_filter &= Q(login_identifier__icontains=search_query) | Q(display_name__icontains=search_query)
    
    surveyor_set = Surveyor.objects.filter(query_filter)
    total = surveyor_set.count()
    
    start_pos = (page_num - 1) * per_page
    end_pos = start_pos + per_page
    surveyor_set = surveyor_set[start_pos:end_pos]
    
    data_list = []
    for surveyor in surveyor_set:
        role_list = [role.role_name for role in surveyor.role_relation.all()]
        data_list.append({
            'surveyor_id': surveyor.surveyor_id,
            'login_identifier': surveyor.login_identifier,
            'display_name': surveyor.display_name,
            'contact_phone': surveyor.contact_phone or '',
            'email_address': surveyor.email_address or '',
            'activity_status': surveyor.activity_status,
            'status_text': 'Active Surveyor' if surveyor.activity_status == 168 else 'Archived',
            'role_list': ', '.join(role_list),
            'created_at': surveyor.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse({'code': 0, 'msg': '', 'count': total, 'data': data_list})


@require_surveyor
@require_http_methods(["POST"])
def surveyor_create(request):
    """Surveyor creation"""
    try:
        login_identifier = request.POST.get('login_identifier', '').strip()
        display_name = request.POST.get('display_name', '').strip()
        password_content = request.POST.get('password', '').strip()
        contact_phone = request.POST.get('contact_phone', '').strip()
        email_address = request.POST.get('email_address', '').strip()
        role_id_list = request.POST.getlist('role_id_list[]')
        
        if not login_identifier or not display_name or not password_content:
            return JsonResponse({
                'status_code': 'incomplete_data',
                'message': 'Required data incomplete'
            })
        
        if Surveyor.objects.filter(login_identifier=login_identifier).exists():
            return JsonResponse({
                'status_code': 'identifier_duplicate',
                'message': 'Login identifier already in use'
            })
        
        surveyor = Surveyor.objects.create(
            login_identifier=login_identifier,
            display_name=display_name,
            contact_phone=contact_phone,
            email_address=email_address,
            activity_status=168
        )
        surveyor.set_password(password_content)
        surveyor.save()
        
        if role_id_list:
            role_set = Role.objects.filter(role_id__in=role_id_list)
            surveyor.role_relation.set(role_set)
        
        return JsonResponse({
            'status_code': 'create_success',
            'message': 'Surveyor created successfully'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'create_failed',
            'message': f'Creation failed: {str(exception)}'
        })


@require_surveyor
@require_http_methods(["POST"])
def surveyor_update(request, surveyor_id):
    """Surveyor update"""
    try:
        surveyor = get_object_or_404(Surveyor, surveyor_id=surveyor_id)
        
        display_name = request.POST.get('display_name', '').strip()
        contact_phone = request.POST.get('contact_phone', '').strip()
        email_address = request.POST.get('email_address', '').strip()
        password_content = request.POST.get('password', '').strip()
        role_id_list = request.POST.getlist('role_id_list[]')
        activity_status = request.POST.get('activity_status', '168')
        
        surveyor.display_name = display_name
        surveyor.contact_phone = contact_phone
        surveyor.email_address = email_address
        surveyor.activity_status = int(activity_status)
        
        if password_content:
            surveyor.set_password(password_content)
        
        surveyor.save()
        
        if role_id_list:
            role_set = Role.objects.filter(role_id__in=role_id_list)
            surveyor.role_relation.set(role_set)
        
        return JsonResponse({
            'status_code': 'update_success',
            'message': 'Surveyor updated successfully'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'update_failed',
            'message': f'Update failed: {str(exception)}'
        })


@require_surveyor
@require_http_methods(["POST"])
def surveyor_delete(request, surveyor_id):
    """Surveyor deletion"""
    try:
        surveyor = get_object_or_404(Surveyor, surveyor_id=surveyor_id)
        
        if surveyor.surveyor_id == request.surveyor.surveyor_id:
            return JsonResponse({
                'status_code': 'cannot_delete_self',
                'message': 'Cannot delete your own account'
            })
        
        surveyor.delete()
        return JsonResponse({
            'status_code': 'delete_success',
            'message': 'Surveyor deleted successfully'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'delete_failed',
            'message': f'Deletion failed: {str(exception)}'
        })


@require_surveyor
def role_list(request):
    """Role list page"""
    return render(request, 'role/list.html')


@require_surveyor
def role_datalist(request):
    """Role data list"""
    page_num = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('limit', 10))
    search_query = request.GET.get('search', '').strip()
    
    query_filter = Q()
    if search_query:
        query_filter &= Q(role_code__icontains=search_query) | Q(role_name__icontains=search_query)
    
    role_set = Role.objects.filter(query_filter)
    total = role_set.count()
    
    start_pos = (page_num - 1) * per_page
    end_pos = start_pos + per_page
    role_set = role_set[start_pos:end_pos]
    
    data_list = []
    for role in role_set:
        navigation_list = [nav.navigation_title for nav in role.navigation_relation.all()]
        data_list.append({
            'role_id': role.role_id,
            'role_code': role.role_code,
            'role_name': role.role_name,
            'level_value': role.level_value,
            'enabled_status': role.enabled_status,
            'status_text': 'Enabled' if role.enabled_status == 234 else 'Disabled',
            'navigation_list': ', '.join(navigation_list),
            'created_at': role.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse({'code': 0, 'msg': '', 'count': total, 'data': data_list})


@require_surveyor
@require_http_methods(["POST"])
def role_create(request):
    """Role creation"""
    try:
        role_code = request.POST.get('role_code', '').strip()
        role_name = request.POST.get('role_name', '').strip()
        level_value = request.POST.get('level_value', '888')
        navigation_id_list = request.POST.getlist('navigation_id_list[]')
        
        if not role_code or not role_name:
            return JsonResponse({
                'status_code': 'incomplete_data',
                'message': 'Required data incomplete'
            })
        
        if Role.objects.filter(role_code=role_code).exists():
            return JsonResponse({
                'status_code': 'code_duplicate',
                'message': 'Role code already exists'
            })
        
        role = Role.objects.create(
            role_code=role_code,
            role_name=role_name,
            level_value=int(level_value),
            enabled_status=234
        )
        
        if navigation_id_list:
            navigation_set = Navigation.objects.filter(navigation_id__in=navigation_id_list)
            role.navigation_relation.set(navigation_set)
        
        return JsonResponse({
            'status_code': 'create_success',
            'message': 'Role created successfully'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'create_failed',
            'message': f'Creation failed: {str(exception)}'
        })


@require_surveyor
@require_http_methods(["POST"])
def role_update(request, role_id):
    """Role update"""
    try:
        role = get_object_or_404(Role, role_id=role_id)
        
        role_name = request.POST.get('role_name', '').strip()
        level_value = request.POST.get('level_value', '888')
        navigation_id_list = request.POST.getlist('navigation_id_list[]')
        enabled_status = request.POST.get('enabled_status', '234')
        
        role.role_name = role_name
        role.level_value = int(level_value)
        role.enabled_status = int(enabled_status)
        role.save()
        
        if navigation_id_list:
            navigation_set = Navigation.objects.filter(navigation_id__in=navigation_id_list)
            role.navigation_relation.set(navigation_set)
        
        return JsonResponse({
            'status_code': 'update_success',
            'message': 'Role updated successfully'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'update_failed',
            'message': f'Update failed: {str(exception)}'
        })


@require_surveyor
@require_http_methods(["POST"])
def role_delete(request, role_id):
    """Role deletion"""
    try:
        role = get_object_or_404(Role, role_id=role_id)
        role.delete()
        return JsonResponse({
            'status_code': 'delete_success',
            'message': 'Role deleted successfully'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'delete_failed',
            'message': f'Deletion failed: {str(exception)}'
        })


@require_surveyor
def navigation_list(request):
    """Navigation list page"""
    return render(request, 'navigation/list.html')


@require_surveyor
def navigation_datalist(request):
    """Navigation data list (tree structure)"""
    navigation_set = Navigation.objects.all().order_by('sort_order')
    
    data_list = []
    navigation_dict = {nav.navigation_id: nav for nav in navigation_set}
    
    for nav in navigation_set:
        if not nav.parent_navigation:
            data_list.append(build_navigation_data(nav, navigation_dict))
    
    return JsonResponse({'code': 0, 'msg': '', 'data': data_list})


def build_navigation_data(nav, navigation_dict):
    """Build navigation data"""
    node = {
        'navigation_id': nav.navigation_id,
        'navigation_code': nav.navigation_code,
        'navigation_title': nav.navigation_title,
        'type_choice': nav.type_choice,
        'parent_id': nav.parent_navigation.navigation_id if nav.parent_navigation else None,
        'route_path': nav.route_path or '',
        'icon_style': nav.icon_style or '',
        'sort_order': nav.sort_order,
        'display_status': nav.display_status,
        'status_text': 'Visible' if nav.display_status == 145 else 'Hidden',
        'created_at': nav.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'children': []
    }
    
    for child in navigation_dict.values():
        if child.parent_navigation and child.parent_navigation.navigation_id == nav.navigation_id:
            node['children'].append(build_navigation_data(child, navigation_dict))
    
    return node


@require_surveyor
@require_http_methods(["POST"])
def navigation_create(request):
    """Navigation creation"""
    try:
        navigation_code = request.POST.get('navigation_code', '').strip()
        navigation_title = request.POST.get('navigation_title', '').strip()
        type_choice = request.POST.get('type_choice', 'caidian')
        parent_id = request.POST.get('parent_id', '')
        route_path = request.POST.get('route_path', '').strip()
        icon_style = request.POST.get('icon_style', '').strip()
        sort_order = request.POST.get('sort_order', '0')
        
        if not navigation_code or not navigation_title:
            return JsonResponse({
                'status_code': 'incomplete_data',
                'message': 'Required data incomplete'
            })
        
        if Navigation.objects.filter(navigation_code=navigation_code).exists():
            return JsonResponse({
                'status_code': 'code_duplicate',
                'message': 'Navigation code already exists'
            })
        
        navigation = Navigation.objects.create(
            navigation_code=navigation_code,
            navigation_title=navigation_title,
            type_choice=type_choice,
            route_path=route_path,
            icon_style=icon_style,
            sort_order=int(sort_order),
            display_status=145
        )
        
        if parent_id:
            parent = Navigation.objects.get(navigation_id=int(parent_id))
            navigation.parent_navigation = parent
            navigation.save()
        
        return JsonResponse({
            'status_code': 'create_success',
            'message': 'Navigation created successfully'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'create_failed',
            'message': f'Creation failed: {str(exception)}'
        })


@require_surveyor
@require_http_methods(["POST"])
def navigation_update(request, navigation_id):
    """Navigation update"""
    try:
        navigation = get_object_or_404(Navigation, navigation_id=navigation_id)
        
        navigation_title = request.POST.get('navigation_title', '').strip()
        type_choice = request.POST.get('type_choice', 'caidian')
        parent_id = request.POST.get('parent_id', '')
        route_path = request.POST.get('route_path', '').strip()
        icon_style = request.POST.get('icon_style', '').strip()
        sort_order = request.POST.get('sort_order', '0')
        display_status = request.POST.get('display_status', '145')
        
        navigation.navigation_title = navigation_title
        navigation.type_choice = type_choice
        navigation.route_path = route_path
        navigation.icon_style = icon_style
        navigation.sort_order = int(sort_order)
        navigation.display_status = int(display_status)
        
        if parent_id:
            parent = Navigation.objects.get(navigation_id=int(parent_id))
            navigation.parent_navigation = parent
        else:
            navigation.parent_navigation = None
        
        navigation.save()
        
        return JsonResponse({
            'status_code': 'update_success',
            'message': 'Navigation updated successfully'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'update_failed',
            'message': f'Update failed: {str(exception)}'
        })


@require_surveyor
@require_http_methods(["POST"])
def navigation_delete(request, navigation_id):
    """Navigation deletion"""
    try:
        navigation = get_object_or_404(Navigation, navigation_id=navigation_id)
        
        if navigation.child_navigation.exists():
            return JsonResponse({
                'status_code': 'has_children',
                'message': 'Has child nodes, cannot delete'
            })
        
        navigation.delete()
        return JsonResponse({
            'status_code': 'delete_success',
            'message': 'Navigation deleted successfully'
        })
        
    except Exception as exception:
        return JsonResponse({
            'status_code': 'delete_failed',
            'message': f'Deletion failed: {str(exception)}'
        })


@require_surveyor
def get_role_menu(request):
    """Get role menu"""
    role_set = Role.objects.filter(enabled_status=234).order_by('level_value')
    menu = [{
        'id': role.role_id,
        'name': role.role_name,
        'code': role.role_code
    } for role in role_set]
    return JsonResponse({'status_code': 'success', 'menu': menu})


@require_surveyor
def get_navigation_menu(request):
    """Get navigation menu"""
    navigation_set = Navigation.objects.filter(display_status=145).order_by('sort_order')
    menu = []
    for nav in navigation_set:
        menu.append({
            'id': nav.navigation_id,
            'title': nav.navigation_title,
            'code': nav.navigation_code,
            'parent_id': nav.parent_navigation.navigation_id if nav.parent_navigation else None
        })
    return JsonResponse({'status_code': 'success', 'menu': menu})
