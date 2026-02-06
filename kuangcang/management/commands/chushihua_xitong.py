from django.core.management.base import BaseCommand
from kuangcang.models import Kanche, Juese, Daohang


class Command(BaseCommand):
    help = '初始化矿藏系统数据'
    
    def handle(self, *args, **options):
        self.stdout.write('开始初始化矿藏系统...')
        
        # 创建导航
        self.stdout.write('创建导航结构...')
        xitong_guanli = Daohang.objects.create(
            daohang_bianma='xitong_guanli',
            daohang_biaoti='系统管理',
            leixing_xuanze='mulu',
            tubiao_yangshi='layui-icon-set',
            paixu_haoma=10,
            xianshi_zhuangtai=145
        )
        
        Daohang.objects.create(
            daohang_bianma='kanche_guanli',
            daohang_biaoti='勘察员管理',
            leixing_xuanze='caidian',
            fuji_daohang=xitong_guanli,
            luyou_dizhi='/kanche/liebiao/',
            tubiao_yangshi='layui-icon-user',
            paixu_haoma=1,
            xianshi_zhuangtai=145
        )
        
        Daohang.objects.create(
            daohang_bianma='juese_guanli',
            daohang_biaoti='角色管理',
            leixing_xuanze='caidian',
            fuji_daohang=xitong_guanli,
            luyou_dizhi='/juese/liebiao/',
            tubiao_yangshi='layui-icon-group',
            paixu_haoma=2,
            xianshi_zhuangtai=145
        )
        
        Daohang.objects.create(
            daohang_bianma='daohang_guanli',
            daohang_biaoti='导航管理',
            leixing_xuanze='caidian',
            fuji_daohang=xitong_guanli,
            luyou_dizhi='/daohang/liebiao/',
            tubiao_yangshi='layui-icon-template',
            paixu_haoma=3,
            xianshi_zhuangtai=145
        )
        
        # 创建角色
        self.stdout.write('创建角色...')
        chaoji_guanliyuan = Juese.objects.create(
            juese_daima='CHAOJI_GUANLIYUAN',
            juese_mingcheng='超级管理员',
            dengji_shuzhi=1,
            qiyong_zhuangtai=234
        )
        
        quanxian_daohang = Daohang.objects.all()
        chaoji_guanliyuan.daohang_guanlian.set(quanxian_daohang)
        
        putong_yonghu = Juese.objects.create(
            juese_daima='PUTONG_YONGHU',
            juese_mingcheng='普通用户',
            dengji_shuzhi=100,
            qiyong_zhuangtai=234
        )
        
        # 创建超级管理员账户
        self.stdout.write('创建超级管理员账户...')
        admin_kanche = Kanche.objects.create(
            denglu_biaoshi='admin',
            mingcheng_xianshi='系统管理员',
            lianxi_dianhua='13800138000',
            dianzi_youjian='admin@dizhi.com',
            huodong_zhuangtai=168
        )
        admin_kanche.shezhi_mima('admin888')
        admin_kanche.save()
        admin_kanche.juese_guanlian.add(chaoji_guanliyuan)
        
        # 创建测试用户
        self.stdout.write('创建测试用户...')
        test_kanche = Kanche.objects.create(
            denglu_biaoshi='test',
            mingcheng_xianshi='测试勘察员',
            lianxi_dianhua='13900139000',
            dianzi_youjian='test@dizhi.com',
            huodong_zhuangtai=168
        )
        test_kanche.shezhi_mima('test123')
        test_kanche.save()
        test_kanche.juese_guanlian.add(putong_yonghu)
        
        self.stdout.write(self.style.SUCCESS('✓ 初始化完成!'))
        self.stdout.write('默认账户:')
        self.stdout.write('  管理员 - 账号: admin, 密码: admin888')
        self.stdout.write('  测试员 - 账号: test, 密码: test123')
