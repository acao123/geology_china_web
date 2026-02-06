# 🚀 快速启动指南

## 一键启动（3步）

```bash
# 步骤1: 安装依赖
pip install -r requirements.txt

# 步骤2: 初始化系统（已完成迁移和数据）
# 如需重新初始化，删除 db.sqlite3 后执行：
python manage.py migrate
python manage.py chushihua_xitong

# 步骤3: 启动服务器
python manage.py runserver 0.0.0.0:8000
```

访问: http://localhost:8000

## 🔑 默认账户

| 账号 | 密码 | 角色 |
|-----|------|-----|
| admin | admin888 | 超级管理员 |
| test | test123 | 普通用户 |

## 📋 功能验证清单

访问系统后，请验证以下功能：

- [ ] 登录页面显示正常
- [ ] 验证码图片生成（点击可刷新）
- [ ] 使用admin/admin888登录成功
- [ ] 中心仪表盘显示4个统计数字
- [ ] 左侧菜单显示系统管理模块
- [ ] 点击"勘察员管理"显示表格数据
- [ ] 点击"角色管理"显示角色列表
- [ ] 点击"导航管理"显示树形导航
- [ ] 退出登录功能正常

## 🛠️ 测试API

```bash
# 1. 获取验证码
curl http://localhost:8000/denglu/yanzhengma/ -o captcha.png

# 2. 登录（需要先获取验证码和CSRF token）
curl -X POST http://localhost:8000/denglu/tijiao/ \
  -H "X-Requested-With: XMLHttpRequest" \
  -d "denglu_biaoshi=admin&mima_neirong=admin888&yanzhengma_shuru=XXXX"

# 3. 获取勘察员列表数据
curl http://localhost:8000/kanche/shujuliu/?page=1&limit=10

# 4. 获取角色列表数据
curl http://localhost:8000/juese/shujuliu/?page=1&limit=10

# 5. 获取导航树形数据
curl http://localhost:8000/daohang/shujuliu/
```

## �� 常见问题

### Q1: 验证码不显示
```bash
pip install Pillow==10.1.0
```

### Q2: 数据库迁移失败
```bash
rm db.sqlite3
rm -rf kuangcang/migrations/0001_*
python manage.py makemigrations
python manage.py migrate
python manage.py chushihua_xitong
```

### Q3: 静态文件404
```bash
mkdir -p jingdian
# 或者使用 CDN 的 Layui（已配置）
```

### Q4: 登录后跳转404
检查模板目录：
```bash
ls -la muban/denglu/
ls -la muban/zhongxin/
```

### Q5: 中间件报错
确认 `dizhi/settings.py` 中的 MIDDLEWARE 配置顺序正确。

## 📊 系统信息

```bash
# 检查系统状态
python manage.py check

# 查看数据库迁移状态
python manage.py showmigrations

# 进入Django Shell
python manage.py shell

# 创建新的勘察员
python manage.py shell
>>> from kuangcang.models import Kanche
>>> kc = Kanche.objects.create(denglu_biaoshi='newuser', mingcheng_xianshi='新用户', huodong_zhuangtai=168)
>>> kc.shezhi_mima('password123')
>>> kc.save()
>>> exit()
```

## 🔒 安全提示

生产环境部署前：
1. 修改 `SECRET_KEY`
2. 设置 `DEBUG = False`
3. 配置 `ALLOWED_HOSTS`
4. 使用 MySQL/PostgreSQL
5. 启用 HTTPS
6. 修改默认密码

## 📞 获取帮助

- 查看 `README.md` 了解详细功能
- 查看 `PROJECT_SUMMARY.md` 了解技术细节
- 检查代码注释了解实现逻辑

---

**祝您使用愉快！** 🎉
