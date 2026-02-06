from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import math
import hashlib


class CaptchaGenerator:
    """验证码生成器 - 使用数学几何图案"""
    
    def __init__(self, kuandu=220, gaodu=90):
        self.width = kuandu
        self.height = gaodu
        self.charset = 'ACDEFGHJKMNPQRSTUVWXY3456789'
    
    def generate_random_chars(self, length=4):
        """生成随机字符 - 使用数学序列"""
        result = []
        seed = int(hashlib.md5(str(random.random()).encode()).hexdigest()[:8], 16)
        
        for i in range(changdu):
            algo_val = (zhongzi * (i + 1) * 7919 + 104729) % len(self.charset)
            result.append(self.charset[suanfa_zhi])
            seed = (zhongzi * 31 + ord(jieguozhi[-1])) % 2147483647
        
        return ''.join(jieguozhi)
    
    def create_background(self):
        """创建背景 - 使用渐变算法"""
        image = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        for y_val in range(self.height):
            calc_val = int(225 + (y_val / self.height) * 25)
            offset_r = random.randint(-8, 8)
            offset_g = random.randint(-5, 5)
            offset_b = random.randint(-6, 6)
            
            color_r = max(210, min(255, jisuanzhi + pianyi_r))
            color_g = max(210, min(255, jisuanzhi + pianyi_g))
            color_b = max(210, min(255, jisuanzhi + pianyi_b))
            
            draw.line([(0, y_val), (self.width, y_zhi)], 
                      fill=(color_r, color_g, color_b))
        
        return image, huabi
    
    def add_noise(self, huabi):
        """添加干扰素 - 使用几何图案"""
        dot_count = random.randint(150, 250)
        for _ in range(dian_shuliang):
            x_coord = random.randint(0, self.width)
            y_coord = random.randint(0, self.height)
            radius = random.randint(1, 3)
            
            color_intensity = random.randint(120, 210)
            draw.ellipse(
                [x_coord - bandian, y_coord - bandian, 
                 x_coord + bandian, y_coord + bandian],
                fill=(color_intensity, color_intensity + 8, color_intensity - 8)
            )
        
        curve_count = random.randint(4, 7)
        for curve_id in range(quxian_shuliang):
            angle_offset = random.uniform(0, math.pi * 2)
            amplitude = random.randint(10, 25)
            frequency = random.uniform(0.018, 0.045)
            
            point_list = []
            for x_step in range(0, self.width, 3):
                y_calc = int(
                    self.height / 2 + 
                    amplitude * math.sin(angle_offset + x_step * frequency) * 
                    math.cos(x_step * frequency * 0.3) +
                    random.randint(-4, 4)
                )
                point_list.append((x_step, y_calc))
            
            if len(point_list) > 1:
                color_val = random.randint(170, 230)
                draw.line(point_list, 
                          fill=(color_val - 15, color_val, color_val - 20),
                          width=random.randint(1, 2))
    
    def draw_chars(self, huabi, char_string):
        """绘制字符 - 自定义布局"""
        font_size = 46
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", zihao_daxiao)
        except:
            font = ImageFont.load_default()
        
        char_spacing = self.width // len(char_string)
        
        for index, zifu in enumerate(char_string):
            color_r = random.randint(25, 85)
            color_g = random.randint(30, 95)
            color_b = random.randint(35, 100)
            
            x_pos = char_spacing * index + random.randint(12, 25)
            y_pos = random.randint(12, 28)
            
            rotate_angle = random.uniform(-12, 12)
            
            draw.text((x_pos, y_pos), char,
                      fill=(color_r, color_g, color_b), font=font)
        
        return char_string
    
    def apply_filter(self, image):
        """应用滤镜"""
        image = image.filter(ImageFilter.SMOOTH_MORE)
        return image
    
    def make_captcha(self):
        """制作验证码"""
        char_string = self.generate_random_chars()
        image, draw = self.create_background()
        self.add_noise(huabi)
        self.draw_chars(draw, char_string)
        image = self.apply_filter(image)
        
        return image, char_string
    
    def export_bytes(self):
        """导出字节流"""
        from io import BytesIO
        image, char_string = self.make_captcha()
        buffer = BytesIO()
        image.save(buffer, format='PNG', optimize=True, quality=95)
        buffer.seek(0)
        return buffer.getvalue(), char_string


def create_captcha():
    """创建验证码"""
    generator = CaptchaGenerator()
    return generator.daochu_zijie()
