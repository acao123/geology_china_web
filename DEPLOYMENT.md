# 生产环境部署指南

## 📋 部署前检查清单

### 1. 环境准备

```bash
# Python 版本要求
python --version  # 需要 3.8+

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置

#### 开发环境（SQLite）
默认配置已就绪，无需修改。

#### 生产环境（MySQL）

修改 `dizhi/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'geology_db',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

创建数据库：
```sql
CREATE DATABASE geology_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 安全配置

修改 `dizhi/settings.py`:

```python
# 生产环境必须修改
DEBUG = False

# 添加你的域名
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# 生成新的密钥
SECRET_KEY = 'your-new-secret-key-here-make-it-very-long-and-random'

# HTTPS 配置（如果使用）
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 4. 静态文件配置

```python
# dizhi/settings.py
STATIC_ROOT = BASE_DIR / 'static_collected'
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'jingdian']

# 收集静态文件
python manage.py collectstatic --noinput
```

### 5. 数据库迁移和初始化

```bash
# 执行迁移
python manage.py migrate

# 初始化系统数据
python manage.py chushihua_xitong

# 创建超级管理员（如果需要额外管理员）
python manage.py createsuperuser
```

## 🚀 部署方式

### 方式一：使用 Gunicorn + Nginx

#### 1. 安装 Gunicorn

```bash
pip install gunicorn
```

#### 2. 创建 Gunicorn 配置

创建 `gunicorn_config.py`:

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
max_requests = 1000
timeout = 30
keepalive = 2
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"
```

#### 3. 启动 Gunicorn

```bash
gunicorn dizhi.wsgi:application -c gunicorn_config.py
```

#### 4. Nginx 配置

创建 `/etc/nginx/sites-available/geology`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 20M;
    
    location /static/ {
        alias /path/to/geology_china_web/static_collected/;
    }
    
    location /media/ {
        alias /path/to/geology_china_web/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/geology /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 方式二：使用 Systemd 服务

创建 `/etc/systemd/system/geology.service`:

```ini
[Unit]
Description=Geology China Web Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/geology_china_web
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn dizhi.wsgi:application -c gunicorn_config.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable geology
sudo systemctl start geology
sudo systemctl status geology
```

## 📊 性能优化

### 1. 数据库优化

```python
# dizhi/settings.py
DATABASES = {
    'default': {
        # ... 其他配置
        'CONN_MAX_AGE': 600,  # 连接池
    }
}
```

### 2. 缓存配置

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# 会话缓存
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### 3. Gzip 压缩

```python
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    # ... 其他中间件
]
```

## 🔒 安全建议

### 1. 定期更新密码

```bash
# 进入 Django shell
python manage.py shell

>>> from kuangcang.models import Kanche
>>> admin = Kanche.objects.get(denglu_biaoshi='admin')
>>> admin.shezhi_mima('new_secure_password')
>>> admin.save()
```

### 2. 日志监控

创建 `dizhi/logging_config.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/geology.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
```

### 3. 备份策略

```bash
# 每日备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/geology"

# 备份数据库
python manage.py dumpdata > $BACKUP_DIR/db_$DATE.json

# 或 MySQL 备份
mysqldump -u user -p geology_db > $BACKUP_DIR/mysql_$DATE.sql
```

## 🎯 常见问题

### Q1: 静态文件 404
```bash
python manage.py collectstatic --clear
```

### Q2: 权限问题
```bash
chown -R www-data:www-data /path/to/geology_china_web
chmod -R 755 /path/to/geology_china_web
```

### Q3: 数据库连接失败
检查 MySQL 用户权限：
```sql
GRANT ALL PRIVILEGES ON geology_db.* TO 'user'@'localhost';
FLUSH PRIVILEGES;
```

## 📞 技术支持

- 查看日志: `tail -f /var/log/gunicorn/error.log`
- 系统检查: `python manage.py check --deploy`
- 测试配置: `python manage.py test`

---

**部署完成后请修改默认密码！**
