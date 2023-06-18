import random
import string
from datetime import datetime
from hashlib import md5

from captcha.image import ImageCaptcha
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from system.models import TUser, Module, Role, Permission, UserRole


# Create your views here.

def index(request):
    return render(request, 'system/index.html')


@xframe_options_exempt
def welcome(request):
    return render(request, 'system/welcome.html')


def login(request):
    # 判断session是否有数据
    if request.session.get('user'):
        return redirect('system:index')
    return render(request, 'system/login.html')


def registry(request):
    """注册页面"""
    return render(request, 'system/registry.html')


def unique_username(request):
    """判断用户名知否存在"""
    try:
        username = request.GET.get('username')
        user = TUser.objects.get(username=username)
        return JsonResponse({'code': 400, 'msg': '用户已存在'})
    except Exception as e:
        return JsonResponse({'code': 200, 'msg': '用户可以使用'})


def captcha(request):
    """构建验证码"""
    code = generate_code()
    image = ImageCaptcha()
    captcha = image.generate(code)

    request.session['code'] = code
    request.session.set_expiry(60)
    return HttpResponse(captcha.getvalue())


def generate_code():
    """生成四位随机验证码"""

    letters = string.ascii_letters  # 得到所有字母

    digits = string.digits  # 得到所有数字

    result = ''

    flag = [1, 0, 'i', 'I', 'l', 'L', 'o', 'O']

    for i in range(4):

        while True:
            char = random.choice(letters + digits)
            if char in flag:
                continue
            else:
                break
        result += char

    return result


def registry_account(request):
    """注册账号"""
    try:
        # 1.拿到前台发送过来的数据：username、password、captcha
        username = request.GET.get('username')
        user = TUser.objects.values('username')
        password = request.GET.get('password')
        captcha = request.GET.get('captcha')
        # 2.拿出存储在session中的验证码
        session_code = request.session.get('code')
        # 2.1.判断验证码是否过期：能取出来就没过期，否则过期
        if not session_code:
            return JsonResponse({'code': 400, 'msg': '验证码已过期'})
        # 2.2.把session的验证码转为大写，和前台发送过来的验证码转为大写判断是否相同
        if session_code.upper() != captcha.upper():
            return JsonResponse({'code': 400, 'msg': '验证码错误'})
        # 3.根据generate_code函数取到随机的盐
        salt = generate_code()
        # 4.把密码和盐一起进行md5加密
        md5_password = md5((password + salt).encode('utf-8')).hexdigest()
        # 5.通过objects里面的save方法来完成保存用户
        user = TUser(username=username, password=md5_password, salt=salt)
        user.save()  # 将数据保存在数据库
        return JsonResponse({'code': 200, 'msg': '注册成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '注册失败'})


def login_account(request):
    """登录账号函数"""
    try:
        # 用户名
        username = request.GET.get('username')
        user = TUser.objects.get(username=username, state=1, isValid=1)

        # 密码
        password = request.GET.get('password')
        salt = user.salt
        md5_password = md5((password + salt).encode('utf-8')).hexdigest()
        password_account = user.password

        # 验证码
        captcha = request.GET.get('captcha')
        session_code = request.session.get('code')
        # 2.1.判断验证码是否过期：能取出来就没过期，否则过期
        if not session_code:
            return JsonResponse({'code': 400, 'msg': '验证码已过期'})
        # 2.2.把session的验证码转为大写，和前台发送过来的验证码转为大写判断是否相同
        if session_code.upper() != captcha.upper():
            return JsonResponse({'code': 400, 'msg': '验证码错误'})

        # 保持登录
        remember = request.GET.get('remember')

        if md5_password == password_account:
            request.session['user'] = {'id': user.id, 'username': user.username}
            # 判断remember的值 1选中保持登录， 0不保持登录
            if remember == '1':
                request.session.set_expiry(60 * 60 * 27 * 7)  # 保持登录七天
            return JsonResponse({'code': 200, 'msg': '登录成功'})
        else:
            return JsonResponse({'code': 400, 'msg': '密码错误'})

    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '用户名错误 或者 用户未审核'})


@xframe_options_exempt
def settings(request):
    """基本资料"""
    try:
        session_user = request.session.get('user')
        id = session_user['id']
        # 根据 id 查询用户信息
        user = TUser.objects.values('id').filter(isValid=1, id=id)

        return render(request, 'system/settings.html', user[0])
    except Exception as e:
        return render(request, 'system/settings.html')


def save_setting(request):
    """修改基本资料信息操作"""
    try:
        id = request.GET.get('id')
        username = request.GET.get('username')
        truename = request.GET.get('truename')
        email = request.GET.get('email')
        phone = request.GET.get('phone')

        user = TUser.objects.get(id=id)

        try:
            if email and email != user.email:
                TUser.objects.get(email=email)
                return JsonResponse({'code': 400, 'msg': '邮箱已存在'})

        except Exception as e:
            pass

        TUser.objects.filter(id=id).update(truename=truename,
                                           email=email,
                                           phone=phone,
                                           updateDate=datetime.now())

        return JsonResponse({'code': 200, 'msg': '操作成功'})

    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '操作失败，请检查用户名是否有误'})


def logout(request):
    request.session.flush()
    return redirect('system:login')


@xframe_options_exempt
def password(request):
    return render(request, 'system/password.html')


def change_password(request):
    """修改密码操作"""
    try:
        # 获取输入的数据
        old_password = request.GET.get('old_password')
        new_password = request.GET.get('new_password')
        again_password = request.GET.get('again_password')

        if new_password != again_password:
            return JsonResponse({'code': 400, 'msg': '两次密码输入不正确'})

        # 查询用户
        session_user = request.session.get('user')
        if session_user is None:
            return JsonResponse({'code': 400, 'msg': '无session信息'})

        # 查询数据库
        user = TUser.objects.get(id=session_user['id'])

        #
        md5_password = md5((old_password + user.salt).encode('utf-8')).hexdigest()

        # 判断old密码是否输入有误
        if user.password != md5_password:
            return JsonResponse({'code': 400, 'msg': '密码输入有误'})

        # 对新密码进行加密
        salt = generate_code()
        md5_password = md5((new_password + salt).encode(encoding='utf-8')).hexdigest()

        # 更新数据
        TUser.objects.filter(id=user.id).update(password=md5_password,
                                                salt=salt,
                                                updateDate=datetime.now())
        return JsonResponse({'code': 200, 'msg': '密码修改成功'})

    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '操作失败'})


@xframe_options_exempt
def audit_account(request):
    """账号审核"""
    try:
        ids = request.GET.getlist('ids')
        state = request.GET.get('state')
        TUser.objects.filter(id__in=ids).update(state=state)
        content = {
            'code': 200,
            'msg': '修改成功'
        }
        return render(request, 'system/audit_account.html', content)

    except Exception as e:
        content = {
            'code': 200,
            'msg': '修改失败'
        }
        return render(request, 'system/audit_account.html', content)


@require_GET
def select_user_list(request):
    try:
        page_num = request.GET.get('page')  # 页号
        page_size = request.GET.get('limit')  # 页容量

        username = request.GET.get('username')
        state = request.GET.get('state')

        if username and state:
            users = TUser.objects.filter(isValid=1, username__icontains=username, state=state).values()
        elif username:
            users = TUser.objects.filter(isValid=1, username__icontains=username).values()
        elif state:
            users = TUser.objects.filter(isValid=1, state=state).values()
        else:
            users = TUser.objects.filter(isValid=1).values()
        paginator = Paginator(users, page_size)
        users_list = paginator.page(page_num).object_list

        user_response = {
            'code': 0,
            'msg': '',
            'count': len(users),
            'data': list(users_list)
        }

        return JsonResponse(user_response)

    except Exception as e:
        return JsonResponse({'code': 400, 'msg': 'error'})


@xframe_options_exempt
@require_GET
def module_index(request):
    """菜单管理首页"""
    return render(request, 'system/module/module.html')


@require_GET
def select_module(request):
    """查询所有模块信息"""
    try:
        # 查询
        # {'模型属性名': 'select DATE_FORMAT(数据库列名, '格式化样式')'}
        select = {'createDate': "select DATE_FORMAT(create_date, '%%Y-%%m-%%d%% H: %% i: %%s')",
                  'updateDate': "select DATE_FORMAT(update_date, '%%Y-%%m-%%d %% H: %% i: %%s')"
                  }
        # 如果使用后台格式化日期，必须将要格式化的列展示在values()参数中
        queryset = Module.objects.extra(select=select).values('id', 'parent',
                                                              'moduleName', 'moduleStyle',
                                                              'optValue', 'url',
                                                              'grade',
                                                              'createDate',
                                                              'updateDate').order_by('id').all()
        return JsonResponse(list(queryset), safe=False)
    except Module.DoesNotExist as e:
        pass


@xframe_options_exempt
@require_GET
def module_create_or_update(request):
    """添加/修改菜单页面"""
    # 获取 grade 和 parentId
    grade = request.GET.get('grade')
    parentId = request.GET.get('parentId')
    context = {
        'grade': grade,
        'parentId': parentId
    }
    # 获取 id 如果存在的话说明是修改
    id = request.GET.get('id')
    if id:
        module = Module.objects.get(pk=id)
        context['module'] = module
        context['parentId'] = module.parent_id
    return render(request, 'system/module/add_update.html', context)


@csrf_exempt
@require_GET
def create_module(request):
    """添加模块信息"""
    global data
    try:
        # 接收参数
        data = request.GET.dict()
        data.pop('id')
        # 如果权限值已存在，提示错误
        optValue = data.get('optValue')

        Module.objects.get(optValue=optValue)
        return JsonResponse({'code': 400, 'msg': '权限值已存在'})
    except Module.DoesNotExist as e:
        pass
    # 如果有父级菜单查询父级对象插入
    parentId = data.pop('parentId')
    if parentId and parentId == '-1':
        pass
    else:
        p = Module.objects.get(pk=parentId)
        data['parent'] = p
    # 添加数据
    Module.objects.create(**data)
    return JsonResponse({'code': 200, 'msg': '添加成功'})


@csrf_exempt
@require_GET
def update_module(request):
    """修改模块信息"""
    global id, data
    try:
        # 接收参数
        data = request.GET.dict()
        data.pop('parentId')
        id = data.pop('id')
        # 如果权限值被修改，判断是否存在，已存在，提示错误
        optValue = data.get('optValue')
        # 查询原来的模块信息
        m = Module.objects.get(pk=id)
        # 判断是否权限值被修改
        if optValue != m.optValue:
            # 判断是否存在
            Module.objects.get(optValue=optValue)
            return JsonResponse({'code': 400, 'msg': '权限值已存在'})
    except Module.DoesNotExist as e:
        pass
    # 修改数据
    Module.objects.filter(pk=id).update(**data, updateDate=datetime.now())
    return JsonResponse({'code': 200, 'msg': '修改成功'})


@csrf_exempt
@require_GET
def delete_module(request):
    """删除模块信息"""
    global id
    try:
        # 接收参数
        id = request.GET.get('id')
        # 查询是否有子项
        Module.objects.get(parent=id)
        return JsonResponse({'code': 400, 'msg': '请先删除子项'})
    except Module.DoesNotExist as e:
        pass
    # 删除模块
    Module.objects.filter(pk=id).delete()
    return JsonResponse({'code': 200, 'msg': '删除成功'})


@xframe_options_exempt
@require_GET
def roel_index(request):
    """角色管理首页"""
    return render(request, 'system/role/role.html')


@require_GET
def select_role(request):
    """查询所有角色信息"""
    try:
        # 获取第几页
        page_num = request.GET.get('page', 1)  # 添加默认值，防止没有参数导致的异常错误
        # 获取每页多少条
        page_size = request.GET.get('limit', 10)  # 添加默认值，防止没有参数导致的异常错误
        # 查询
        # {'模型属性名': 'select DATE_FORMAT(数据库列名, '格式化样式')'}
        select = {'createDate': "select DATE_FORMAT(create_date, '%%Y-%%m-%%d%%H:%%i:%%s')",
                  'updateDate': "select DATE_FORMAT(update_date, '%%Y-%%m-%%d%%H:%%i:%%s')"
                  }
        # 如果使用后台格式化日期，必须将要格式化的列展示在values()参数中
        queryset = Role.objects.extra(select=select).values('id', 'roleName',
                                                            'roleRemark',
                                                            'createDate',
                                                            'updateDate').order_by('-id').all()
        # 带条件查询
        roleName = request.GET.get('roleName')
        if roleName:
            queryset = queryset.filter(roleName__icontains=roleName)
        # 初始化分页对象
        p = Paginator(queryset, page_size)
        # 获取指定页数的数据
        data = p.page(page_num).object_list
        # 返回总条数
        count = p.count
        # 返回数据，按照 layuimini 要求格式构建
        context = {
            'code': 0,
            'msg': '',
            'count': count,
            'data': list(data)
        }
        return JsonResponse(context)
    except Module.DoesNotExist as e:
        pass


@xframe_options_exempt
@require_GET
def role_create_or_update(request):
    """添加/修改角色页面"""
    # 获取角色主键
    id = request.GET.get('id')
    context = None
    if id:
        context = {'role': Role.objects.get(pk=id)}
    return render(request, 'system/role/add_update.html', context)


@csrf_exempt
@require_GET
def create_role(request):
    """添加角色信息"""
    global data
    try:
        # 接收参数
        data = request.GET.dict()
        data.pop('id')
        # 如果角色已存在，提示错误
        roleName = data.get('roleName')
        Role.objects.get(roleName=roleName)
        return JsonResponse({'code': 400, 'msg': '角色名已存在'})
    except Role.DoesNotExist as e:
        pass
    # 添加数据
    Role.objects.create(**data)
    return JsonResponse({'code': 200, 'msg': '添加成功'})


@csrf_exempt
@require_GET
def update_role(request):
    """修改角色信息"""
    global data, id
    try:
        # 接收参数
        data = request.GET.dict()
        id = data.pop('id')
        # 如果角色被修改，判断是否存在，已存在，提示错误
        roleName = data.get('roleName')
        # 查询原来的角色信息
        r = Role.objects.get(pk=id)
        # 判断角色是否被修改
        if roleName != r.roleName:
            # 判断是否存在
            Role.objects.get(roleName=roleName)
            return JsonResponse({'code': 400, 'msg': '角色名已存在'})
    except Role.DoesNotExist as e:
        pass
    # 修改数据
    data['updateDate'] = datetime.now()
    Role.objects.filter(pk=id).update(**data)
    return JsonResponse({'code': 200, 'msg': '修改成功'})


@xframe_options_exempt
@require_GET
def role_grant(request):
    """跳转角色授权页面"""
    # 获取角色主键
    id = request.GET.get('id')
    context = {'id': id}
    return render(request, 'system/role/grant.html', context)


@require_GET
def select_role_module(request):
    """查询所有权限及当前角色所拥有的权限"""
    # 获取角色主键
    roleId = request.GET.get('id')
    # 查询所有权限(模块)
    module = list(Module.objects.values('id', 'parent', 'moduleName').all())
    # 查询角色已拥有的权限(资源)
    roleModule = Permission.objects.values_list('module',
                                                flat=True).filter(role__id=roleId).all()
    # 设置 checked
    for m in module:
        if m.get('id') in roleModule:
            m['checked'] = 'true'
        else:
            m['checked'] = 'false'
    # 返回数据
    return JsonResponse(module, safe=False)


@csrf_exempt
@require_GET
def role_relate_module(request):
    """角色关联模块"""
    try:
        # 接收参数
        module_checked_id = request.GET.get('module_checked_id')
        role_id = request.GET.get('role_id')
        # 删除该角色拥有的所有权限
        Permission.objects.filter(role__id=role_id).delete()
        # 如果模块为空，则直接 return
        if not module_checked_id:
            return JsonResponse({'code': 200, 'msg': '操作成功'})
        # 查询角色和模块
        role = Role.objects.get(pk=role_id)
        module = Module.objects.filter(pk__in=module_checked_id.split(',')).all()
        # 循环插入数据
        for m in module:
            Permission.objects.create(role=role, module=m)
        return JsonResponse({'code': 200, 'msg': '操作成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '操作失败'})


@xframe_options_exempt
@require_GET
def user_index(request):
    """用户管理首页"""
    return render(request, 'system/user/user.html')


@require_GET
def select_user(request):
    """查询所有用户信息"""
    try:
        # 获取第几页
        page_num = request.GET.get('page', 1)  # 添加默认值，防止没有参数导致的异常错误
        # 获取每页多少条
        page_size = request.GET.get('limit', 10)  # 添加默认值，防止没有参数导致的异常错误
        # 查询
        # {'模型属性名': 'select DATE_FORMAT(数据库列名, '格式化样式')'}
        select = {'create_date': "select DATE_FORMAT(create_date, '%%Y-%%m-%%d%%H:%%i:%%s')",
                  'update_date': "select DATE_FORMAT(update_date, '%%Y-%%m-%%d%%H:%%i:%%s')"
                  }
        # 如果使用后台格式化日期，必须将要格式化的列展示在values()参数中
        queryset = TUser.objects.extra(select=select).values('id', 'username',
                                                             'truename', 'email', 'phone',
                                                             'create_date',
                                                             'update_date').order_by('-id').all()
        # 接收参数，按条件查询
        username = request.GET.get('username')
        if username:
            queryset = queryset.filter(username__icontains=username)
        email = request.GET.get('email')
        if email:
            queryset = queryset.filter(email__icontains=email)
        phone = request.GET.get('phone')
        if phone:
            queryset = queryset.filter(phone__icontains=phone)
        # 初始化分页对象
        p = Paginator(queryset, page_size)
        # 获取指定页数的数据
        data = p.page(page_num).object_list
        # 返回总条数
        count = p.count
        # 返回数据，按照 layuimini 要求格式构建
        context = {
            'code': 0,
            'msg': '',
            'count': count,
            'data': list(data)
        }
        return JsonResponse(context)
    except TUser.DoesNotExist as e:
        pass


@xframe_options_exempt
@require_GET
def user_create_or_update(request):
    """跳转添加或修改用户页面"""
    # 获取用户主键
    id = request.GET.get('id')
    context = None
    if id:
        context = {'user': TUser.objects.get(id=id)}
    return render(request, 'system/user/add_update.html', context)


@require_GET
def select_role_for_user(request):
    """用户管理查询角色"""
    try:
        # 查询所有角色
        role = Role.objects.values('id', 'roleName').all().order_by('id')
        # 返回数据
        context = {'role': list(role)}
        # 获取用户主键
        id = request.GET.get('id')
        if id:
            # 查询用户所有角色
            roleIds = UserRole.objects.values_list('role', flat=True).filter(user__id=id).all()
            userRole = Role.objects.values('id', 'roleName').filter(pk__in=roleIds).all()
            context['userRole'] = list(userRole)
        return JsonResponse(context, safe=False)
    except Role.DoesNotExist as e:
        pass


def create_userrole(role_ids, user, is_create=False):
    """添加用户角色中间表"""
    if not is_create:
        # 删除所有该用户的角色
        # user.userrole_set.all().delete()
        UserRole.objects.filter(user__id=user.id).delete()
    try:
        if len(role_ids) > 0:
            roles = Role.objects.filter(pk__in=role_ids.split(',')).all()
            for role in roles:
                UserRole.objects.create(user=user, role=role)
        return {'code': 200, 'msg': '操作成功'}
    except Exception as e:
        return {'code': 200, 'msg': '操作成功1'}


@csrf_exempt
@require_GET
def create_user(request):
    """添加用户信息"""
    # global data
    try:
        # 接收参数
        data = request.GET.dict()
        # print(data)
        data.pop('id')
        # 如果用户名已存在，提示错误
        username = data.get('username')
        TUser.objects.get(username=username)
        return JsonResponse({'code': 400, 'msg': '该用户已存在'})
    except TUser.DoesNotExist as e:
        pass

    try:
        # 如果邮箱已存在，提示错误
        email = data.get('email')
        TUser.objects.get(email=email)
        return JsonResponse({'code': 400, 'msg': '邮箱已存在，请重新添加'})
    except TUser.DoesNotExist as e:
        pass
    # 加密密码
    # 使用md5加密
    data['password'] = md5('123456'.encode(encoding='utf-8')).hexdigest()
    if 'select' in data:
        role_ids = data.pop('select')
    else:
        role_ids = None
    # 添加数据
    user = TUser.objects.create(**data)
    '''
    # 插入用户角色中间表
    if len(role_ids) > 0:
        roles = Role.objects.filter(pk__in=role_ids.split(',')).all()
        for role in roles:
            UserRole.objects.create(user=user, role=role)
    '''
    # 插入用户角色中间表
    result = create_userrole(role_ids, user, is_create=True)
    return JsonResponse(result)


@csrf_exempt
@require_GET
def update_user(request):
    """修改用户信息"""
    try:
        # 接收参数
        data = request.GET.dict()
        id = data.pop('id')
        user = TUser.objects.get(id=id)
        username = data.get('username')
        # 如果用户名被更改，判断用户名是否存在
        if username and username != user.username:
            TUser.objects.get(username=username)
        return JsonResponse({'code': 200, 'msg': '用户名已存在，请重新添加'})
    except TUser.DoesNotExist as e:
        pass
    try:
        # 如果邮箱被更改，判断邮箱是否存在
        email = data.get('email')
        if email and email != user.email:
            TUser.objects.get(email=email)
            return JsonResponse({'code': 200, 'msg': '邮箱已存在，请重新添加'})
    except TUser.DoesNotExist as e:
        pass
    if 'select' in data:
        role_ids = data.pop('select')
    else:
        role_ids = None
    '''
    # 删除所有该用户的角色
    UserRole.objects.filter(user__id=id).delete()
    
    if len(role_ids) > 0:
        # 修改用户角色中间表
        roles = Role.objects.filter(pk__in=role_ids.split(',')).all()
        for role in roles:
            UserRole.objects.create(user=user, role=role)
    '''
    # 修改数据
    data['updateDate'] = datetime.now()
    TUser.objects.filter(id=id).update(**data)
    # 修改用户角色中间表
    result = create_userrole(role_ids, user)
    return JsonResponse(result)


@csrf_exempt
@require_GET
def delete_user(request):
    """删除用户信息"""
    # 接收参数
    ids = request.GET.getlist('ids')
    # 逻辑删除
    TUser.objects.filter(pk__in=ids).update(isValid=0, updateDate=datetime.now())
    # 删除用户所有角色
    UserRole.objects.filter(user__id__in=ids).delete()
    return JsonResponse({'code': 200, 'msg': '删除成功'})


@require_GET
def select_customer_manager(request):
    """查询客户经理（指派人）"""
    user_list = TUser.objects.values("id", 'username', 'truename') \
        .filter(isValid=1).order_by('-id').all()
    return JsonResponse(list(user_list), safe=False)