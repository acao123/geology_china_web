from django.db import models
import hashlib
import secrets
import base64


def yanzheng_jiami(yuanshi_mima):
    """验证加密 - 独特的三重哈希算法"""
    yansui_1 = secrets.token_urlsafe(32)
    yansui_2 = secrets.token_urlsafe(16)
    
    hunhe_1 = hashlib.sha3_384(f"{yuanshi_mima}{yansui_1}".encode()).hexdigest()
    hunhe_2 = hashlib.blake2b(f"{hunhe_1}{yansui_2}".encode(), digest_size=32).hexdigest()
    hunhe_3 = hashlib.sha512(f"{hunhe_2}{yansui_1[:8]}".encode()).hexdigest()
    
    zuhe = f"{yansui_1}#{yansui_2}#{hunhe_3}"
    return base64.urlsafe_b64encode(zuhe.encode()).decode()


def yanzheng_duibi(yuanshi_mima, jiami_wenben):
    """验证对比 - 三重验证"""
    try:
        jiemi = base64.urlsafe_b64decode(jiami_wenben.encode()).decode()
        bufeng = jiemi.split('#')
        if len(bufeng) != 3:
            return False
        
        yansui_1, yansui_2, cunchu_hash = bufeng
        
        hunhe_1 = hashlib.sha3_384(f"{yuanshi_mima}{yansui_1}".encode()).hexdigest()
        hunhe_2 = hashlib.blake2b(f"{hunhe_1}{yansui_2}".encode(), digest_size=32).hexdigest()
        hunhe_3 = hashlib.sha512(f"{hunhe_2}{yansui_1[:8]}".encode()).hexdigest()
        
        return hunhe_3 == cunchu_hash
    except:
        return False


class Kanche(models.Model):
    """勘察员模型"""
    HUODONG_ZHUANGTAI = ((168, '活跃勘察'), (37, '休眠封存'))
    
    kanche_bianhao = models.AutoField(primary_key=True, db_column='kc_id')
    denglu_biaoshi = models.CharField(max_length=120, unique=True, db_column='dl_bs')
    mingcheng_xianshi = models.CharField(max_length=200, db_column='mc_xs')
    jiami_mima = models.CharField(max_length=800, db_column='jm_mm')
    lianxi_dianhua = models.CharField(max_length=40, null=True, blank=True, db_column='lx_dh')
    dianzi_youjian = models.CharField(max_length=200, null=True, blank=True, db_column='dz_yj')
    touxiang_lujing = models.CharField(max_length=800, null=True, blank=True, db_column='tx_lj')
    huodong_zhuangtai = models.IntegerField(choices=HUODONG_ZHUANGTAI, default=168, db_column='hd_zt')
    juese_guanlian = models.ManyToManyField('Juese', blank=True, related_name='kanche_jh', db_column='js_gl')
    zuijin_denglu = models.DateTimeField(null=True, blank=True, db_column='zj_dl')
    chuangjian_shijian = models.DateTimeField(auto_now_add=True, db_column='cj_sj')
    xiugai_shijian = models.DateTimeField(auto_now=True, db_column='xg_sj')
    beizhu_xinxi = models.TextField(null=True, blank=True, db_column='bz_xx')
    
    class Meta:
        db_table = 'kuang_kanche'
        ordering = ['-chuangjian_shijian']
        indexes = [
            models.Index(fields=['denglu_biaoshi'], name='idx_kc_denglu'),
            models.Index(fields=['huodong_zhuangtai'], name='idx_kc_zhuangtai'),
        ]
    
    def __str__(self):
        return f"勘察:{self.mingcheng_xianshi}[{self.denglu_biaoshi}]"
    
    def shezhi_mima(self, yuanshi_mima):
        """设置密码"""
        self.jiami_mima = yanzheng_jiami(yuanshi_mima)
    
    def yanzheng_mima(self, yuanshi_mima):
        """验证密码"""
        return yanzheng_duibi(yuanshi_mima, self.jiami_mima)
    
    def shifou_huodong(self):
        """是否活跃"""
        return self.huodong_zhuangtai == 168


class Juese(models.Model):
    """角色模型"""
    QIYONG_ZHUANGTAI = ((234, '启用状态'), (56, '禁用状态'))
    
    juese_bianhao = models.AutoField(primary_key=True, db_column='js_id')
    juese_daima = models.CharField(max_length=120, unique=True, db_column='js_dm')
    juese_mingcheng = models.CharField(max_length=200, db_column='js_mc')
    dengji_shuzhi = models.IntegerField(default=888, db_column='dj_sz')
    qiyong_zhuangtai = models.IntegerField(choices=QIYONG_ZHUANGTAI, default=234, db_column='qy_zt')
    daohang_guanlian = models.ManyToManyField('Daohang', blank=True, related_name='juese_jh', db_column='dh_gl')
    chuangjian_shijian = models.DateTimeField(auto_now_add=True, db_column='cj_sj')
    xiugai_shijian = models.DateTimeField(auto_now=True, db_column='xg_sj')
    beizhu_xinxi = models.TextField(null=True, blank=True, db_column='bz_xx')
    
    class Meta:
        db_table = 'kuang_juese'
        ordering = ['dengji_shuzhi', '-chuangjian_shijian']
        indexes = [
            models.Index(fields=['juese_daima'], name='idx_js_daima'),
            models.Index(fields=['dengji_shuzhi'], name='idx_js_dengji'),
        ]
    
    def __str__(self):
        return f"角色:{self.juese_mingcheng}({self.juese_daima})"
    
    def shifou_qiyong(self):
        """是否启用"""
        return self.qiyong_zhuangtai == 234


class Daohang(models.Model):
    """导航模型"""
    LEIXING_XUANZE = (('mulu', '目录类型'), ('caidian', '菜单类型'), ('anniu', '按钮类型'))
    XIANSHI_ZHUANGTAI = ((145, '显示状态'), (48, '隐藏状态'))
    
    daohang_bianhao = models.AutoField(primary_key=True, db_column='dh_id')
    daohang_bianma = models.CharField(max_length=120, unique=True, db_column='dh_bm')
    daohang_biaoti = models.CharField(max_length=200, db_column='dh_bt')
    leixing_xuanze = models.CharField(max_length=40, choices=LEIXING_XUANZE, default='caidian', db_column='lx_xz')
    fuji_daohang = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='ziji_daohang', db_column='fj_dh')
    luyou_dizhi = models.CharField(max_length=800, null=True, blank=True, db_column='ly_dz')
    tubiao_yangshi = models.CharField(max_length=200, null=True, blank=True, db_column='tb_ys')
    paixu_haoma = models.IntegerField(default=0, db_column='px_hm')
    xianshi_zhuangtai = models.IntegerField(choices=XIANSHI_ZHUANGTAI, default=145, db_column='xs_zt')
    chuangjian_shijian = models.DateTimeField(auto_now_add=True, db_column='cj_sj')
    xiugai_shijian = models.DateTimeField(auto_now=True, db_column='xg_sj')
    beizhu_xinxi = models.TextField(null=True, blank=True, db_column='bz_xx')
    
    class Meta:
        db_table = 'kuang_daohang'
        ordering = ['paixu_haoma', 'daohang_bianhao']
        indexes = [
            models.Index(fields=['daohang_bianma'], name='idx_dh_bianma'),
            models.Index(fields=['paixu_haoma'], name='idx_dh_paixu'),
        ]
    
    def __str__(self):
        return f"导航:{self.daohang_biaoti}[{self.daohang_bianma}]"
    
    def shifou_xianshi(self):
        """是否显示"""
        return self.xianshi_zhuangtai == 145
    
    def huoqu_ziji(self):
        """获取子集"""
        return Daohang.objects.filter(fuji_daohang=self, xianshi_zhuangtai=145).order_by('paixu_haoma')
    
    def goujian_lujing(self):
        """构建路径"""
        if self.fuji_daohang:
            return f"{self.fuji_daohang.goujian_lujing()}▶{self.daohang_biaoti}"
        return self.daohang_biaoti


class Caozuo(models.Model):
    """操作日志模型"""
    caozuo_bianhao = models.AutoField(primary_key=True, db_column='cz_id')
    kanche_yinyong = models.ForeignKey(Kanche, on_delete=models.SET_NULL, null=True, db_column='kc_yy')
    mokuai_mingcheng = models.CharField(max_length=200, db_column='mk_mc')
    caozuo_leixing = models.CharField(max_length=120, db_column='cz_lx')
    caozuo_miaoshu = models.TextField(db_column='cz_ms')
    qingqiu_fangshi = models.CharField(max_length=20, db_column='qq_fs')
    qingqiu_lujing = models.CharField(max_length=800, db_column='qq_lj')
    qingqiu_ip = models.CharField(max_length=120, db_column='qq_ip')
    caozuo_shijian = models.DateTimeField(auto_now_add=True, db_column='cz_sj')
    
    class Meta:
        db_table = 'kuang_caozuo'
        ordering = ['-caozuo_shijian']
        indexes = [
            models.Index(fields=['-caozuo_shijian'], name='idx_cz_shijian'),
        ]
    
    def __str__(self):
        return f"操作:{self.mokuai_mingcheng}-{self.caozuo_leixing}"

