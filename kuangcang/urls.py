from django.urls import path
from kuangcang import views

urlpatterns = [
    path('denglu/xianshi/', views.login_display, name='denglu_xianshi'),
    path('denglu/tijiao/', views.login_submit, name='denglu_tijiao'),
    path('denglu/likakai/', views.login_logout, name='denglu_likakai'),
    path('denglu/yanzhengma/', views.login_captcha, name='denglu_yanzhengma'),
    
    path('zhongxin/', views.center_display, name='zhongxin_xianshi'),
    
    path('kanche/liebiao/', views.surveyor_list, name='kanche_liebiao'),
    path('kanche/shujuliu/', views.surveyor_datalist, name='kanche_shujuliu'),
    path('kanche/chuangjian/', views.surveyor_create, name='kanche_chuangjian'),
    path('kanche/xiugai/<int:surveyor_id>/', views.surveyor_update, name='kanche_xiugai'),
    path('kanche/shanchu/<int:surveyor_id>/', views.surveyor_delete, name='kanche_shanchu'),
    
    path('juese/liebiao/', views.role_list, name='juese_liebiao'),
    path('juese/shujuliu/', views.role_datalist, name='juese_shujuliu'),
    path('juese/chuangjian/', views.role_create, name='juese_chuangjian'),
    path('juese/xiugai/<int:role_id>/', views.role_update, name='juese_xiugai'),
    path('juese/shanchu/<int:role_id>/', views.role_delete, name='juese_shanchu'),
    
    path('daohang/liebiao/', views.navigation_list, name='daohang_liebiao'),
    path('daohang/shujuliu/', views.navigation_datalist, name='daohang_shujuliu'),
    path('daohang/chuangjian/', views.navigation_create, name='daohang_chuangjian'),
    path('daohang/xiugai/<int:navigation_id>/', views.navigation_update, name='daohang_xiugai'),
    path('daohang/shanchu/<int:navigation_id>/', views.navigation_delete, name='daohang_shanchu'),
    
    path('api/juese/mulu/', views.get_role_menu, name='huoqu_juese_mulu'),
    path('api/daohang/mulu/', views.get_navigation_menu, name='huoqu_daohang_mulu'),
]
