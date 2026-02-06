from django.core.management.base import BaseCommand
from kuangcang.models import Surveyor, Role, Navigation


class Command(BaseCommand):
    help = 'Initialize mine system data'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting mine system initialization...')
        
        # Create navigation
        self.stdout.write('Creating navigation structure...')
        system_management = Navigation.objects.create(
            navigation_code='system_management',
            navigation_title='System Management',
            type_choice='mulu',
            icon_style='layui-icon-set',
            sort_order=10,
            display_status=145
        )
        
        Navigation.objects.create(
            navigation_code='surveyor_management',
            navigation_title='Surveyor Management',
            type_choice='caidian',
            parent_navigation=system_management,
            route_path='/surveyor/list/',
            icon_style='layui-icon-user',
            sort_order=1,
            display_status=145
        )
        
        Navigation.objects.create(
            navigation_code='role_management',
            navigation_title='Role Management',
            type_choice='caidian',
            parent_navigation=system_management,
            route_path='/role/list/',
            icon_style='layui-icon-group',
            sort_order=2,
            display_status=145
        )
        
        Navigation.objects.create(
            navigation_code='navigation_management',
            navigation_title='Navigation Management',
            type_choice='caidian',
            parent_navigation=system_management,
            route_path='/navigation/list/',
            icon_style='layui-icon-template',
            sort_order=3,
            display_status=145
        )
        
        # Create roles
        self.stdout.write('Creating roles...')
        super_admin = Role.objects.create(
            role_code='SUPER_ADMIN',
            role_name='Super Administrator',
            level_value=1,
            enabled_status=234
        )
        
        all_navigation = Navigation.objects.all()
        super_admin.navigation_relation.set(all_navigation)
        
        regular_user = Role.objects.create(
            role_code='REGULAR_USER',
            role_name='Regular User',
            level_value=100,
            enabled_status=234
        )
        
        # Create super admin account
        self.stdout.write('Creating super admin account...')
        admin_surveyor = Surveyor.objects.create(
            login_identifier='admin',
            display_name='System Administrator',
            contact_phone='13800138000',
            email_address='admin@geology.com',
            activity_status=168
        )
        admin_surveyor.set_password('admin888')
        admin_surveyor.save()
        admin_surveyor.role_relation.add(super_admin)
        
        # Create test user
        self.stdout.write('Creating test user...')
        test_surveyor = Surveyor.objects.create(
            login_identifier='test',
            display_name='Test Surveyor',
            contact_phone='13900139000',
            email_address='test@geology.com',
            activity_status=168
        )
        test_surveyor.set_password('test123')
        test_surveyor.save()
        test_surveyor.role_relation.add(regular_user)
        
        self.stdout.write(self.style.SUCCESS('✓ Initialization complete!'))
        self.stdout.write('Default accounts:')
        self.stdout.write('  Admin - Login: admin, Password: admin888')
        self.stdout.write('  Test  - Login: test, Password: test123')
