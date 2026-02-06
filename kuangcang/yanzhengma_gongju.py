from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import math
import hashlib


class YanzhengmaShengchengqi:
    """验证码生成器 - 使用数学几何图案"""
    
    def __init__(self, kuandu=220, gaodu=90):
        self.kuandu = kuandu
        self.gaodu = gaodu
        self.zifu_ku = 'ACDEFGHJKMNPQRSTUVWXY3456789'
    
    def shengcheng_suiji_zifu(self, changdu=4):
        """生成随机字符 - 使用数学序列"""
        jieguozhi = []
        zhongzi = int(hashlib.md5(str(random.random()).encode()).hexdigest()[:8], 16)
        
        for i in range(changdu):
            suanfa_zhi = (zhongzi * (i + 1) * 7919 + 104729) % len(self.zifu_ku)
            jieguozhi.append(self.zifu_ku[suanfa_zhi])
            zhongzi = (zhongzi * 31 + ord(jieguozhi[-1])) % 2147483647
        
        return ''.join(jieguozhi)
    
    def chuangjian_beijing(self):
        """创建背景 - 使用渐变算法"""
        tupian = Image.new('RGB', (self.kuandu, self.gaodu), (255, 255, 255))
        huabi = ImageDraw.Draw(tupian)
        
        for y_zhi in range(self.gaodu):
            jisuanzhi = int(225 + (y_zhi / self.gaodu) * 25)
            pianyi_r = random.randint(-8, 8)
            pianyi_g = random.randint(-5, 5)
            pianyi_b = random.randint(-6, 6)
            
            yanse_r = max(210, min(255, jisuanzhi + pianyi_r))
            yanse_g = max(210, min(255, jisuanzhi + pianyi_g))
            yanse_b = max(210, min(255, jisuanzhi + pianyi_b))
            
            huabi.line([(0, y_zhi), (self.kuandu, y_zhi)], 
                      fill=(yanse_r, yanse_g, yanse_b))
        
        return tupian, huabi
    
    def tianjia_ganraosu(self, huabi):
        """添加干扰素 - 使用几何图案"""
        dian_shuliang = random.randint(150, 250)
        for _ in range(dian_shuliang):
            x_zuobiao = random.randint(0, self.kuandu)
            y_zuobiao = random.randint(0, self.gaodu)
            bandian = random.randint(1, 3)
            
            yanse_qiangdu = random.randint(120, 210)
            huabi.ellipse(
                [x_zuobiao - bandian, y_zuobiao - bandian, 
                 x_zuobiao + bandian, y_zuobiao + bandian],
                fill=(yanse_qiangdu, yanse_qiangdu + 8, yanse_qiangdu - 8)
            )
        
        quxian_shuliang = random.randint(4, 7)
        for quxian_id in range(quxian_shuliang):
            jiaodu_pianyi = random.uniform(0, math.pi * 2)
            zhenfu = random.randint(10, 25)
            pinlv = random.uniform(0.018, 0.045)
            
            dian_liebie = []
            for x_bu in range(0, self.kuandu, 3):
                y_jisuan = int(
                    self.gaodu / 2 + 
                    zhenfu * math.sin(jiaodu_pianyi + x_bu * pinlv) * 
                    math.cos(x_bu * pinlv * 0.3) +
                    random.randint(-4, 4)
                )
                dian_liebie.append((x_bu, y_jisuan))
            
            if len(dian_liebie) > 1:
                yanse_zhi = random.randint(170, 230)
                huabi.line(dian_liebie, 
                          fill=(yanse_zhi - 15, yanse_zhi, yanse_zhi - 20),
                          width=random.randint(1, 2))
    
    def huizhi_zifu(self, huabi, zifu_chuang):
        """绘制字符 - 自定义布局"""
        zihao_daxiao = 46
        try:
            ziti = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", zihao_daxiao)
        except:
            ziti = ImageFont.load_default()
        
        zifu_jianju = self.kuandu // len(zifu_chuang)
        
        for suoyin, zifu in enumerate(zifu_chuang):
            yanse_r = random.randint(25, 85)
            yanse_g = random.randint(30, 95)
            yanse_b = random.randint(35, 100)
            
            x_weizhi = zifu_jianju * suoyin + random.randint(12, 25)
            y_weizhi = random.randint(12, 28)
            
            xuanzhuan_jiaodu = random.uniform(-12, 12)
            
            huabi.text((x_weizhi, y_weizhi), zifu,
                      fill=(yanse_r, yanse_g, yanse_b), font=ziti)
        
        return zifu_chuang
    
    def yingyong_lvjing(self, tupian):
        """应用滤镜"""
        tupian = tupian.filter(ImageFilter.SMOOTH_MORE)
        return tupian
    
    def zhizuo_yanzhengma(self):
        """制作验证码"""
        zifu_chuang = self.shengcheng_suiji_zifu()
        tupian, huabi = self.chuangjian_beijing()
        self.tianjia_ganraosu(huabi)
        self.huizhi_zifu(huabi, zifu_chuang)
        tupian = self.yingyong_lvjing(tupian)
        
        return tupian, zifu_chuang
    
    def daochu_zijie(self):
        """导出字节流"""
        from io import BytesIO
        tupian, zifu_chuang = self.zhizuo_yanzhengma()
        huanchong = BytesIO()
        tupian.save(huanchong, format='PNG', optimize=True, quality=95)
        huanchong.seek(0)
        return huanchong.getvalue(), zifu_chuang


def chuangjian_yanzhengma():
    """创建验证码"""
    shengchengqi = YanzhengmaShengchengqi()
    return shengchengqi.daochu_zijie()
