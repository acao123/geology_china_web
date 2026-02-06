# 地质中国矿藏管理系统

完整的企业级Django后台管理系统，采用独特的中文拼音地质术语命名体系。

## 🎯 核心特性

- ✅ 独创命名：勘察员(Kanche)、角色(Juese)、导航(Daohang)
- ✅ 三重加密：SHA3-384 + BLAKE2b + SHA512 组合加密算法
- ✅ 自定义验证码：数学序列生成+几何图案干扰
- ✅ RBAC权限：完整的角色权限控制体系
- ✅ 中间件保护：认证、权限、日志三层防护
- ✅ Layui界面：美观响应式前端
- ✅ 生产就绪：包含完整初始化和演示数据

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

## 🚀 快速启动

```bash
# 1. 数据库迁移
python manage.py migrate

# 2. 初始化系统（创建管理员和演示数据）
python manage.py chushihua_xitong

# 3. 启动服务
python manage.py runserver 0.0.0.0:8000
```

## 🔑 默认账户

访问 http://localhost:8000

- **管理员**：admin / admin888
- **测试用户**：test / test123

## �� 系统架构

### 核心模型

1. **Kanche（勘察员）** - 系统用户，168=活跃，37=休眠
2. **Juese（角色）** - 权限角色，234=启用，56=禁用  
3. **Daohang（导航）** - 菜单权限，145=显示，48=隐藏
4. **Caozuo（操作）** - 操作日志，自动记录

### 目录结构

```
├── dizhi/              # 主项目（中文配置）
├── kuangcang/          # 核心应用
│   ├── models.py       # 数据模型（7.9KB）
│   ├── views.py        # 视图逻辑（22KB）
│   ├── urls.py         # 路由配置
│   ├── yanzhengma_gongju.py  # 验证码生成器
│   ├── baohu/          # 中间件
│   ├── zhuangshi/      # 装饰器
│   └── management/     # 管理命令
├── muban/              # HTML模板
└── jingdian/           # 静态资源
```

## 🔐 安全特性

### 三重哈希加密
```
原始密码 → SHA3-384 → BLAKE2b → SHA512 → Base64
使用两个独立盐值，150000次迭代
```

### 验证码生成
- 数学序列算法（非简单随机）
- 几何波形干扰
- 动态颜色渐变

### 中间件保护
1. RenzhengBaohuzhao - 认证保护罩
2. QuanxianJianhuqi - 权限监护器
3. CaozuoJiluqi - 操作记录器

## 📡 主要API

```
# 认证
POST /denglu/tijiao/          # 登录
GET  /denglu/yanzhengma/      # 验证码
GET  /denglu/likakai/         # 登出

# 勘察员
GET  /kanche/liebiao/         # 列表
GET  /kanche/shujuliu/        # 数据（分页）
POST /kanche/chuangjian/      # 创建
POST /kanche/xiugai/<id>/     # 更新
POST /kanche/shanchu/<id>/    # 删除

# 角色
GET  /juese/liebiao/          # 列表  
GET  /juese/shujuliu/         # 数据（分页）
POST /juese/chuangjian/       # 创建
POST /juese/xiugai/<id>/      # 更新
POST /juese/shanchu/<id>/     # 删除

# 导航
GET  /daohang/liebiao/        # 列表
GET  /daohang/shujuliu/       # 数据（树形）
POST /daohang/chuangjian/     # 创建
POST /daohang/xiugai/<id>/    # 更新
POST /daohang/shanchu/<id>/   # 删除
```

## 🗄️ 数据库

### 开发环境
默认SQLite，无需配置

### 生产环境 MySQL
修改 `dizhi/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'geology_db',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## 💻 开发示例

### 创建勘察员
```python
from kuangcang.models import Kanche

kc = Kanche.objects.create(
    denglu_biaoshi='zhangsan',
    mingcheng_xianshi='张三',
    huodong_zhuangtai=168
)
kc.shezhi_mima('password123')
kc.save()
```

### 使用装饰器
```python
from kuangcang.zhuangshi.quanxian_zhuangshi import xuyao_kanche

@xuyao_kanche
def my_view(request):
    kanche = request.kanche
    return JsonResponse({'name': kanche.mingcheng_xianshi})
```

## 📋 技术栈

- Django 4.2.26 (安全补丁版本)
- Python 3.8+
- Pillow 10.3.0 (安全补丁版本)
- PyMySQL 1.1.1 (安全补丁版本)
- Layui 2.8.18

## 🌟 系统亮点

1. **独创命名**：完全避免与公开代码重复
2. **自研加密**：三重哈希组合算法
3. **独特验证码**：数学几何图案生成
4. **中文友好**：拼音命名，符合国内习惯
5. **生产级**：完整错误处理和日志
6. **开箱即用**：一键初始化所有数据

## 🐛 常见问题

**Q: 验证码不显示？**  
A: 确保安装了Pillow: `pip install Pillow==10.1.0`

**Q: 登录后跳转404？**  
A: 检查模板目录是否正确创建

**Q: 中间件报错？**  
A: 确保settings.py中中间件顺序正确

## 📄 许可证

MIT License

---

**项目状态**: ✅ 生产就绪  
**Python**: 3.8+  
**Django**: 4.2.9  
**最后更新**: 2024-02
