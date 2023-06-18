from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'system'

urlpatterns = [
    # 首页
    path('', views.index, name='index'),
    path('welcome/', views.welcome, name='welcome'),

    # 登录
    path('login/', views.login, name='login'),
    path('login_account/', views.login_account, name='login_account'),

    # 注册
    path('registry/', views.registry, name='registry'),
    path('registry_account/', views.registry_account, name='registry_account'),

    # 重复用户名
    path('unique_username/', views.unique_username, name='unique_username'),

    # 验证码
    path('captcha/', views.captcha, name='captcha'),

    # 设置基本信息
    path('settings/', views.settings, name='settings'),
    path('save_setting/', views.save_setting, name='save_setting'),

    # 退出登录
    path('logout/', views.logout, name='logout'),

    # 修改密码
    path('password/', views.password, name='password'),
    path('change_password/', views.change_password, name='change_password'),

    # 账号审核
    # path('account/', views.account, name='account'),
    path('audit_account/', views.audit_account, name='audit_account'),
    path('select_user_list/', views.select_user_list, name='select_user_list'),

    # 查询菜单
    path('module/', views.module_index, name='module_index'),
    path('module/list/', views.select_module, name='select_module'),

    # 添加/修改菜单
    path('module/create_or_update/', views.module_create_or_update,
         name='module_create_or_update'),
    path('module/create/', views.create_module, name='create_module'),
    path('module/update/', views.update_module, name='update_module'),

    # 删除模块
    path('module/delete/', views.delete_module, name='delete_module'),

    # 查询角色
    path('role/', views.roel_index, name='roel_index'),
    path('role/list/', views.select_role, name='select_role'),

    # 添加/修改角色
    path('role/create_or_update/', views.role_create_or_update,
         name='role_create_or_update'),
    path('role/create/', views.create_role, name='create_role'),
    path('role/update/', views.update_role, name='update_role'),

    # 角色授权
    path('role/grant/', views.role_grant, name='role_grant'),
    path('role/module/', views.select_role_module, name='select_role_module'),
    path('role/grant/add/', views.role_relate_module, name='role_relate_module'),

    # 查询用户
    path('user/', views.user_index, name='user_index'),
    path('user/list/', views.select_user, name='select_user'),

    # 添加用户
    path('user/create_or_update/', views.user_create_or_update,
         name='user_create_or_update'),
    path('user/role/', views.select_role_for_user, name='select_role_for_user'),
    path('user/create/', views.create_user, name='create_user'),

    # 修改用户
    path('user/update/', views.update_user, name='update_user'),

    # 删除用户
    path('user/delete/', views.delete_user, name='delete_user'),

    path('customer_manager/', views.select_customer_manager,
         name='select_customer_manager'),
]
