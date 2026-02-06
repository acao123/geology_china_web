from django.db import models
import hashlib
import secrets
import base64


def verify_encrypt(raw_password):
    """Password encryption - unique triple hash algorithm"""
    salt_1 = secrets.token_urlsafe(32)
    salt_2 = secrets.token_urlsafe(16)
    
    hash_1 = hashlib.sha3_384(f"{raw_password}{salt_1}".encode()).hexdigest()
    hash_2 = hashlib.blake2b(f"{hash_1}{salt_2}".encode(), digest_size=32).hexdigest()
    hash_3 = hashlib.sha512(f"{hash_2}{salt_1[:8]}".encode()).hexdigest()
    
    combination = f"{salt_1}#{salt_2}#{hash_3}"
    return base64.urlsafe_b64encode(combination.encode()).decode()


def verify_compare(raw_password, encrypted_text):
    """Password verification - triple verification"""
    try:
        decrypt = base64.urlsafe_b64decode(encrypted_text.encode()).decode()
        parts = decrypt.split('#')
        if len(parts) != 3:
            return False
        
        salt_1, salt_2, stored_hash = parts
        
        hash_1 = hashlib.sha3_384(f"{raw_password}{salt_1}".encode()).hexdigest()
        hash_2 = hashlib.blake2b(f"{hash_1}{salt_2}".encode(), digest_size=32).hexdigest()
        hash_3 = hashlib.sha512(f"{hash_2}{salt_1[:8]}".encode()).hexdigest()
        
        return hash_3 == stored_hash
    except:
        return False


class Surveyor(models.Model):
    """Surveyor model"""
    ACTIVITY_STATUS = ((168, 'Active Surveyor'), (37, 'Archived'))
    
    surveyor_id = models.AutoField(primary_key=True, db_column='kc_id')
    login_identifier = models.CharField(max_length=120, unique=True, db_column='dl_bs')
    display_name = models.CharField(max_length=200, db_column='mc_xs')
    encrypted_password = models.CharField(max_length=800, db_column='jm_mm')
    contact_phone = models.CharField(max_length=40, null=True, blank=True, db_column='lx_dh')
    email_address = models.CharField(max_length=200, null=True, blank=True, db_column='dz_yj')
    avatar_path = models.CharField(max_length=800, null=True, blank=True, db_column='tx_lj')
    activity_status = models.IntegerField(choices=ACTIVITY_STATUS, default=168, db_column='hd_zt')
    role_relation = models.ManyToManyField('Role', blank=True, related_name='surveyor_set', db_column='js_gl')
    last_login = models.DateTimeField(null=True, blank=True, db_column='zj_dl')
    created_at = models.DateTimeField(auto_now_add=True, db_column='cj_sj')
    updated_at = models.DateTimeField(auto_now=True, db_column='xg_sj')
    notes = models.TextField(null=True, blank=True, db_column='bz_xx')
    
    class Meta:
        db_table = 'kuang_kanche'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['login_identifier'], name='idx_kc_denglu'),
            models.Index(fields=['activity_status'], name='idx_kc_zhuangtai'),
        ]
    
    def __str__(self):
        return f"Surveyor:{self.display_name}[{self.login_identifier}]"
    
    def set_password(self, raw_password):
        """Set password"""
        self.encrypted_password = verify_encrypt(raw_password)
    
    def verify_password(self, raw_password):
        """Verify password"""
        return verify_compare(raw_password, self.encrypted_password)
    
    def is_active(self):
        """Check if active"""
        return self.activity_status == 168


class Role(models.Model):
    """Role model"""
    ENABLED_STATUS = ((234, 'Enabled'), (56, 'Disabled'))
    
    role_id = models.AutoField(primary_key=True, db_column='js_id')
    role_code = models.CharField(max_length=120, unique=True, db_column='js_dm')
    role_name = models.CharField(max_length=200, db_column='js_mc')
    level_value = models.IntegerField(default=888, db_column='dj_sz')
    enabled_status = models.IntegerField(choices=ENABLED_STATUS, default=234, db_column='qy_zt')
    navigation_relation = models.ManyToManyField('Navigation', blank=True, related_name='role_set', db_column='dh_gl')
    created_at = models.DateTimeField(auto_now_add=True, db_column='cj_sj')
    updated_at = models.DateTimeField(auto_now=True, db_column='xg_sj')
    notes = models.TextField(null=True, blank=True, db_column='bz_xx')
    
    class Meta:
        db_table = 'kuang_juese'
        ordering = ['level_value', '-created_at']
        indexes = [
            models.Index(fields=['role_code'], name='idx_js_daima'),
            models.Index(fields=['level_value'], name='idx_js_dengji'),
        ]
    
    def __str__(self):
        return f"Role:{self.role_name}({self.role_code})"
    
    def is_enabled(self):
        """Check if enabled"""
        return self.enabled_status == 234


class Navigation(models.Model):
    """Navigation model"""
    TYPE_CHOICES = (('mulu', 'Directory'), ('caidian', 'Menu'), ('anniu', 'Button'))
    DISPLAY_STATUS = ((145, 'Visible'), (48, 'Hidden'))
    
    navigation_id = models.AutoField(primary_key=True, db_column='dh_id')
    navigation_code = models.CharField(max_length=120, unique=True, db_column='dh_bm')
    navigation_title = models.CharField(max_length=200, db_column='dh_bt')
    type_choice = models.CharField(max_length=40, choices=TYPE_CHOICES, default='caidian', db_column='lx_xz')
    parent_navigation = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='child_navigation', db_column='fj_dh')
    route_path = models.CharField(max_length=800, null=True, blank=True, db_column='ly_dz')
    icon_style = models.CharField(max_length=200, null=True, blank=True, db_column='tb_ys')
    sort_order = models.IntegerField(default=0, db_column='px_hm')
    display_status = models.IntegerField(choices=DISPLAY_STATUS, default=145, db_column='xs_zt')
    created_at = models.DateTimeField(auto_now_add=True, db_column='cj_sj')
    updated_at = models.DateTimeField(auto_now=True, db_column='xg_sj')
    notes = models.TextField(null=True, blank=True, db_column='bz_xx')
    
    class Meta:
        db_table = 'kuang_daohang'
        ordering = ['sort_order', 'navigation_id']
        indexes = [
            models.Index(fields=['navigation_code'], name='idx_dh_bianma'),
            models.Index(fields=['sort_order'], name='idx_dh_paixu'),
        ]
    
    def __str__(self):
        return f"Navigation:{self.navigation_title}[{self.navigation_code}]"
    
    def is_visible(self):
        """Check if visible"""
        return self.display_status == 145
    
    def get_children(self):
        """Get children"""
        return Navigation.objects.filter(parent_navigation=self, display_status=145).order_by('sort_order')
    
    def build_path(self):
        """Build path"""
        if self.parent_navigation:
            return f"{self.parent_navigation.build_path()}▶{self.navigation_title}"
        return self.navigation_title


class Operation(models.Model):
    """Operation log model"""
    operation_id = models.AutoField(primary_key=True, db_column='cz_id')
    surveyor_ref = models.ForeignKey(Surveyor, on_delete=models.SET_NULL, null=True, db_column='kc_yy')
    module_name = models.CharField(max_length=200, db_column='mk_mc')
    operation_type = models.CharField(max_length=120, db_column='cz_lx')
    operation_desc = models.TextField(db_column='cz_ms')
    request_method = models.CharField(max_length=20, db_column='qq_fs')
    request_path = models.CharField(max_length=800, db_column='qq_lj')
    request_ip = models.CharField(max_length=120, db_column='qq_ip')
    operation_time = models.DateTimeField(auto_now_add=True, db_column='cz_sj')
    
    class Meta:
        db_table = 'kuang_caozuo'
        ordering = ['-operation_time']
        indexes = [
            models.Index(fields=['-operation_time'], name='idx_cz_shijian'),
        ]
    
    def __str__(self):
        return f"Operation:{self.module_name}-{self.operation_type}"


# Backward compatibility aliases
Kanche = Surveyor
Juese = Role
Daohang = Navigation
Caozuo = Operation

