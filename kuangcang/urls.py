from django.urls import path
from kuangcang import views

urlpatterns = [
    path('denglu/xianshi/', views.denglu_xianshi, name='denglu_xianshi'),
    path('denglu/tijiao/', views.denglu_tijiao, name='denglu_tijiao'),
    path('denglu/likakai/', views.denglu_likakai, name='denglu_likakai'),
    path('denglu/yanzhengma/', views.denglu_yanzhengma, name='denglu_yanzhengma'),
    
    path('zhongxin/', views.zhongxin_xianshi, name='zhongxin_xianshi'),
    
    path('kanche/liebiao/', views.kanche_liebiao, name='kanche_liebiao'),
    path('kanche/shujuliu/', views.kanche_shujuliu, name='kanche_shujuliu'),
    path('kanche/chuangjian/', views.kanche_chuangjian, name='kanche_chuangjian'),
    path('kanche/xiugai/<int:kanche_bianhao>/', views.kanche_xiugai, name='kanche_xiugai'),
    path('kanche/shanchu/<int:kanche_bianhao>/', views.kanche_shanchu, name='kanche_shanchu'),
    
    path('juese/liebiao/', views.juese_liebiao, name='juese_liebiao'),
    path('juese/shujuliu/', views.juese_shujuliu, name='juese_shujuliu'),
    path('juese/chuangjian/', views.juese_chuangjian, name='juese_chuangjian'),
    path('juese/xiugai/<int:juese_bianhao>/', views.juese_xiugai, name='juese_xiugai'),
    path('juese/shanchu/<int:juese_bianhao>/', views.juese_shanchu, name='juese_shanchu'),
    
    path('daohang/liebiao/', views.daohang_liebiao, name='daohang_liebiao'),
    path('daohang/shujuliu/', views.daohang_shujuliu, name='daohang_shujuliu'),
    path('daohang/chuangjian/', views.daohang_chuangjian, name='daohang_chuangjian'),
    path('daohang/xiugai/<int:daohang_bianhao>/', views.daohang_xiugai, name='daohang_xiugai'),
    path('daohang/shanchu/<int:daohang_bianhao>/', views.daohang_shanchu, name='daohang_shanchu'),
    
    path('api/juese/mulu/', views.huoqu_juese_mulu, name='huoqu_juese_mulu'),
    path('api/daohang/mulu/', views.huoqu_daohang_mulu, name='huoqu_daohang_mulu'),
]
