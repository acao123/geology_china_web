from django.urls import path
from kuangcang import views

urlpatterns = [
    path('login/display/', views.login_display, name='login_display'),
    path('login/submit/', views.login_submit, name='login_submit'),
    path('login/logout/', views.login_logout, name='login_logout'),
    path('login/captcha/', views.login_captcha, name='login_captcha'),
    
    path('center/', views.center_display, name='center_display'),
    
    path('surveyor/list/', views.surveyor_list, name='surveyor_list'),
    path('surveyor/datalist/', views.surveyor_datalist, name='surveyor_datalist'),
    path('surveyor/create/', views.surveyor_create, name='surveyor_create'),
    path('surveyor/update/<int:surveyor_id>/', views.surveyor_update, name='surveyor_update'),
    path('surveyor/delete/<int:surveyor_id>/', views.surveyor_delete, name='surveyor_delete'),
    
    path('role/list/', views.role_list, name='role_list'),
    path('role/datalist/', views.role_datalist, name='role_datalist'),
    path('role/create/', views.role_create, name='role_create'),
    path('role/update/<int:role_id>/', views.role_update, name='role_update'),
    path('role/delete/<int:role_id>/', views.role_delete, name='role_delete'),
    
    path('navigation/list/', views.navigation_list, name='navigation_list'),
    path('navigation/datalist/', views.navigation_datalist, name='navigation_datalist'),
    path('navigation/create/', views.navigation_create, name='navigation_create'),
    path('navigation/update/<int:navigation_id>/', views.navigation_update, name='navigation_update'),
    path('navigation/delete/<int:navigation_id>/', views.navigation_delete, name='navigation_delete'),
    
    path('api/role/menu/', views.get_role_menu, name='get_role_menu'),
    path('api/navigation/menu/', views.get_navigation_menu, name='get_navigation_menu'),
]
