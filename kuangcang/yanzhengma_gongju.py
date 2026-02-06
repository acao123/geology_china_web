from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import math
import hashlib


class CaptchaGenerator:
    """Captcha generator - uses mathematical geometric patterns"""
    
    def __init__(self, width=220, height=90):
        self.width = width
        self.height = height
        self.char_set = 'ACDEFGHJKMNPQRSTUVWXY3456789'
    
    def generate_random_chars(self, length=4):
        """Generate random characters - uses mathematical sequences"""
        result = []
        seed = int(hashlib.md5(str(random.random()).encode()).hexdigest()[:8], 16)
        
        for i in range(length):
            algorithm_value = (seed * (i + 1) * 7919 + 104729) % len(self.char_set)
            result.append(self.char_set[algorithm_value])
            seed = (seed * 31 + ord(result[-1])) % 2147483647
        
        return ''.join(result)
    
    def create_background(self):
        """Create background - uses gradient algorithm"""
        image = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        canvas = ImageDraw.Draw(image)
        
        for y_value in range(self.height):
            calc_value = int(225 + (y_value / self.height) * 25)
            offset_r = random.randint(-8, 8)
            offset_g = random.randint(-5, 5)
            offset_b = random.randint(-6, 6)
            
            color_r = max(210, min(255, calc_value + offset_r))
            color_g = max(210, min(255, calc_value + offset_g))
            color_b = max(210, min(255, calc_value + offset_b))
            
            canvas.line([(0, y_value), (self.width, y_value)], 
                      fill=(color_r, color_g, color_b))
        
        return image, canvas
    
    def add_noise(self, canvas):
        """Add noise - uses geometric patterns"""
        dot_count = random.randint(150, 250)
        for _ in range(dot_count):
            x_coord = random.randint(0, self.width)
            y_coord = random.randint(0, self.height)
            radius = random.randint(1, 3)
            
            color_intensity = random.randint(120, 210)
            canvas.ellipse(
                [x_coord - radius, y_coord - radius, 
                 x_coord + radius, y_coord + radius],
                fill=(color_intensity, color_intensity + 8, color_intensity - 8)
            )
        
        curve_count = random.randint(4, 7)
        for curve_id in range(curve_count):
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
                color_value = random.randint(170, 230)
                canvas.line(point_list, 
                          fill=(color_value - 15, color_value, color_value - 20),
                          width=random.randint(1, 2))
    
    def draw_chars(self, canvas, char_string):
        """Draw characters - custom layout"""
        font_size = 46
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        char_spacing = self.width // len(char_string)
        
        for index, char in enumerate(char_string):
            color_r = random.randint(25, 85)
            color_g = random.randint(30, 95)
            color_b = random.randint(35, 100)
            
            x_position = char_spacing * index + random.randint(12, 25)
            y_position = random.randint(12, 28)
            
            rotation_angle = random.uniform(-12, 12)
            
            canvas.text((x_position, y_position), char,
                      fill=(color_r, color_g, color_b), font=font)
        
        return char_string
    
    def apply_filter(self, image):
        """Apply filter"""
        image = image.filter(ImageFilter.SMOOTH_MORE)
        return image
    
    def make_captcha(self):
        """Make captcha"""
        char_string = self.generate_random_chars()
        image, canvas = self.create_background()
        self.add_noise(canvas)
        self.draw_chars(canvas, char_string)
        image = self.apply_filter(image)
        
        return image, char_string
    
    def export_bytes(self):
        """Export byte stream"""
        from io import BytesIO
        image, char_string = self.make_captcha()
        buffer = BytesIO()
        image.save(buffer, format='PNG', optimize=True, quality=95)
        buffer.seek(0)
        return buffer.getvalue(), char_string


def create_captcha():
    """Create captcha"""
    generator = CaptchaGenerator()
    return generator.export_bytes()
