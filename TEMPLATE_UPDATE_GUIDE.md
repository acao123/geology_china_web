# Template Update Guide

## Overview
The Python code has been fully refactored to use English naming conventions. However, the HTML template **content** still contains Pinyin references that need to be updated to match the new Python code.

## Files Requiring Template Content Updates

### 1. muban/login/display.html
**Current Issues:**
- Form field names use Pinyin: `denglu_biaoshi`, `mima_neirong`, `yanzhengma_shuru`
- Hardcoded URLs: `/denglu/yanzhengma/`, `/denglu/tijiao/`
- JavaScript response keys: `zhuangtai_ma`, `tishi_xinxi`, `tiaozhuan_dizhi`

**Required Changes:**
```html
<!-- OLD -->
<input type="text" name="denglu_biaoshi" placeholder="账号" class="layui-input">
<input type="password" name="mima_neirong" placeholder="密码" class="layui-input">
<input type="text" name="yanzhengma_shuru" placeholder="验证码" class="layui-input">
<img src="/denglu/yanzhengma/" ...>
fetch('/denglu/tijiao/', ...)

<!-- NEW -->
<input type="text" name="login_identifier" placeholder="账号" class="layui-input">
<input type="password" name="password" placeholder="密码" class="layui-input">
<input type="text" name="captcha" placeholder="验证码" class="layui-input">
<img src="{% url 'login_captcha' %}" ...>
fetch("{% url 'login_submit' %}", ...)
```

**JavaScript Updates:**
```javascript
// OLD
if(result.zhuangtai_ma === 'denglu_chenggong') {
    layer.msg(result.tishi_xinxi, ...);
    window.location.href = result.tiaozhuan_dizhi;
}

// NEW
if(result.status_code === 'login_success') {
    layer.msg(result.message, ...);
    window.location.href = result.redirect_url;
}
```

### 2. muban/center/display.html
**Current Issues:**
- Template variables: `{{kanche.mingcheng_xianshi}}`, `{{tongji_shuju}}`, `{{daohang_shuju}}`
- Hardcoded URL: `/denglu/likakai/`
- Variable references: `mokuai_mingcheng`, `caozuo_leixing`, `qingqiu_ip`, `caozuo_shijian`

**Required Changes:**
```html
<!-- OLD -->
<div class="user">👤 {{kanche.mingcheng_xianshi}} | <a href="/denglu/likakai/">退出</a></div>
{{tongji_shuju.kanche_shuliang}}
{{tongji_shuju.juese_shuliang}}
{{tongji_shuju.daohang_shuliang}}
{% for nav in daohang_shuju %}
    <a href="{{nav.luyou}}">{{nav.biaoti}}</a>
{% endfor %}
{{log.mokuai_mingcheng}}
{{log.caozuo_leixing}}
{{log.qingqiu_ip}}
{{log.caozuo_shijian}}

<!-- NEW -->
<div class="user">👤 {{surveyor.display_name}} | <a href="{% url 'login_logout' %}">退出</a></div>
{{stats_data.surveyor_count}}
{{stats_data.role_count}}
{{stats_data.navigation_count}}
{% for nav in navigation_tree %}
    <a href="{{nav.route}}">{{nav.title}}</a>
{% endfor %}
{{log.module_name}}
{{log.operation_type}}
{{log.request_ip}}
{{log.operation_time}}
```

### 3. muban/surveyor/list.html
**Current Issues:**
- Hardcoded URLs: `/zhongxin/`, `/denglu/likakai/`, `/kanche/shujuliu/`
- Table field names: `kanche_bianhao`, `denglu_biaoshi`, `mingcheng_xianshi`, etc.

**Required Changes:**
```html
<!-- OLD -->
<a href="/zhongxin/">返回首页</a>
<a href="/denglu/likakai/">退出</a>
url: '/kanche/shujuliu/'
{field:'kanche_bianhao', title:'ID'}
{field:'denglu_biaoshi', title:'登录账号'}
{field:'mingcheng_xianshi', title:'显示名称'}
{field:'lianxi_dianhua', title:'联系电话'}
{field:'zhuangtai_wenzi', title:'状态'}
{field:'juese_liebiao', title:'角色'}
{field:'chuangjian_shijian', title:'创建时间'}

<!-- NEW -->
<a href="{% url 'center_display' %}">返回首页</a>
<a href="{% url 'login_logout' %}">退出</a>
url: "{% url 'surveyor_datalist' %}"
{field:'surveyor_id', title:'ID'}
{field:'login_identifier', title:'登录账号'}
{field:'display_name', title:'显示名称'}
{field:'contact_phone', title:'联系电话'}
{field:'status_text', title:'状态'}
{field:'role_list', title:'角色'}
{field:'created_at', title:'创建时间'}
```

### 4. muban/role/list.html
**Current Issues:**
- Hardcoded URLs: `/zhongxin/`, `/juese/shujuliu/`
- Table field names: `juese_bianhao`, `juese_daima`, `juese_mingcheng`, etc.

**Required Changes:**
```html
<!-- OLD -->
<a href="/zhongxin/">返回首页</a>
url: '/juese/shujuliu/'
{field:'juese_bianhao', title:'ID'}
{field:'juese_daima', title:'角色代码'}
{field:'juese_mingcheng', title:'角色名称'}
{field:'dengji_shuzhi', title:'等级'}
{field:'zhuangtai_wenzi', title:'状态'}
{field:'daohang_liebiao', title:'导航权限'}
{field:'chuangjian_shijian', title:'创建时间'}

<!-- NEW -->
<a href="{% url 'center_display' %}">返回首页</a>
url: "{% url 'role_datalist' %}"
{field:'role_id', title:'ID'}
{field:'role_code', title:'角色代码'}
{field:'role_name', title:'角色名称'}
{field:'level_value', title:'等级'}
{field:'status_text', title:'状态'}
{field:'navigation_list', title:'导航权限'}
{field:'created_at', title:'创建时间'}
```

### 5. muban/navigation/list.html
**Current Issues:**
- Hardcoded URLs: `/zhongxin/`, `/daohang/shujuliu/`
- Table field names: `daohang_bianhao`, `daohang_bianma`, `daohang_biaoti`, etc.

**Required Changes:**
```html
<!-- OLD -->
<a href="/zhongxin/">返回首页</a>
fetch('/daohang/shujuliu/')
{field:'daohang_bianhao', title:'ID'}
{field:'daohang_bianma', title:'编码'}
{field:'daohang_biaoti', title:'标题'}
{field:'leixing_xuanze', title:'类型'}
{field:'luyou_dizhi', title:'路由'}
{field:'paixu_haoma', title:'排序'}
{field:'zhuangtai_wenzi', title:'状态'}

<!-- NEW -->
<a href="{% url 'center_display' %}">返回首页</a>
fetch("{% url 'navigation_datalist' %}")
{field:'navigation_id', title:'ID'}
{field:'navigation_code', title:'编码'}
{field:'navigation_title', title:'标题'}
{field:'type_choice', title:'类型'}
{field:'route_path', title:'路由'}
{field:'sort_order', title:'排序'}
{field:'status_text', title:'状态'}
```

## Best Practices

1. **Use Django URL Template Tag**: Always use `{% url 'url_name' %}` instead of hardcoded URLs
2. **Load Static Files**: Use `{% load static %}` and `{% static 'path' %}` for static resources
3. **CSRF Token**: Keep `{% csrf_token %}` in all forms
4. **Consistent Naming**: Match Python variable names in templates

## Testing After Updates

1. Start development server: `python manage.py runserver`
2. Test login functionality
3. Test all CRUD operations for surveyors, roles, and navigation
4. Verify all links and redirects work correctly
5. Check browser console for JavaScript errors

## Additional Notes

- The Django templates will automatically escape HTML content for security
- Use browser developer tools to debug AJAX requests
- Check network tab to verify correct URLs are being called
- Console errors will help identify mismatched variable names
