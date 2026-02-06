from django.core.management.base import BaseCommand
from kuangcang.models import Surveyor, Role, Navigation


class Command(BaseCommand):
    help = '初始化矿藏系统数据'
    
    def handle(self, *args, **options):
        self.stdout.write('开始初始化矿藏系统...')
        
        # 创建导航
        self.stdout.write('创建导航结构...')
        system_management = Navigation.objects.create(
            navigation_code='xitong_guanli',
            navigation_title='系统管理',
            type_choice='mulu',
            icon_style='layui-icon-set',
            sort_order=10,
            display_status=145
        )
        
        Navigation.objects.create(
            navigation_code='kanche_guanli',
            navigation_title='勘察员管理',
            type_choice='caidian',
            parent_navigation=system_management,
            route_path='/kanche/liebiao/',
            icon_style='layui-icon-user',
            sort_order=1,
            display_status=145
        )
        
        Navigation.objects.create(
            navigation_code='juese_guanli',
            navigation_title='角色管理',
            type_choice='caidian',
            parent_navigation=system_management,
            route_path='/juese/liebiao/',
            icon_style='layui-icon-group',
            sort_order=2,
            display_status=145
        )
        
        Navigation.objects.create(
            navigation_code='daohang_guanli',
            navigation_title='导航管理',
            type_choice='caidian',
            parent_navigation=system_management,
            route_path='/daohang/liebiao/',
            icon_style='layui-icon-template',
            sort_order=3,
            display_status=145
        )
        
        # 创建角色
        self.stdout.write('创建角色...')
        super_admin = Role.objects.create(
            role_code='CHAOJI_GUANLIYUAN',
            role_name='超级管理员',
            level_value=1,
            enabled_status=234
        )
        
        all_navigations = Navigation.objects.all()
        super_admin.navigation_relation.set(all_navigations)
        
        regular_user = Role.objects.create(
            role_code='PUTONG_YONGHU',
            role_name='普通用户',
            level_value=100,
            enabled_status=234
        )
        
        # 创建超级管理员账户
        self.stdout.write('创建超级管理员账户...')
        admin_surveyor = Surveyor.objects.create(
            login_identifier='admin',
            display_name='系统管理员',
            contact_phone='13800138000',
            email_address='admin@dizhi.com',
            activity_status=168
        )
        admin_surveyor.set_password('admin888')
        admin_surveyor.save()
        admin_surveyor.role_relation.add(super_admin)
        
        # 创建测试用户
        self.stdout.write('创建测试用户...')
        test_surveyor = Surveyor.objects.create(
            login_identifier='test',
            display_name='测试勘察员',
            contact_phone='13900139000',
            email_address='test@dizhi.com',
            activity_status=168
        )
        test_surveyor.set_password('test123')
        test_surveyor.save()
        test_surveyor.role_relation.add(regular_user)
        
        self.stdout.write(self.style.SUCCESS('✓ 初始化完成!'))
        self.stdout.write('默认账户:')
        self.stdout.write('  管理员 - 账号: admin, 密码: admin888')
        self.stdout.write('  测试员 - 账号: test, 密码: test123')
