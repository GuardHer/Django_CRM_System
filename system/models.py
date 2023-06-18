from django.db import models
from datetime import datetime


# Create your models here.


class ModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(isValid=1)


class TUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    salt = models.CharField(max_length=4)
    truename = models.CharField(max_length=20, null=True)
    phone = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=30, null=True)

    # 用户状态, 0为未审核，1为通过审核，-1为黑名单
    state = models.IntegerField(default=0)
    # 是否合法，1合法，0为不合法
    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date', default=datetime.now())
    updateDate = models.DateTimeField(db_column='update_date', null=True)

    objects = ModelManager()

    class Meta:
        db_table = 't_user'


# 资源表
class Module(models.Model):
    # 资源名称
    moduleName = models.CharField(max_length=50, db_column='module_name')
    # 样式
    moduleStyle = models.CharField(max_length=120, db_column='module_style')
    # 跳转地址
    url = models.CharField(max_length=100, db_column='url')
    # 自关联
    parent = models.ForeignKey('self', db_column='parent_id', db_constraint=False,
                               on_delete=models.DO_NOTHING, default=-1)
    # 父级操作值
    parentOptValue = models.CharField(max_length=20, db_column='parent_opt_value')
    # 级别
    grade = models.IntegerField(db_column='grade')
    # 操作值
    optValue = models.CharField(max_length=20, db_column='opt_value')
    # 排序顺序
    orders = models.IntegerField(db_column='orders')
    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date', auto_now_add=True)
    updateDate = models.DateTimeField(max_length=20, db_column='update_date',
                                      auto_now_add=True)
    objects = ModelManager()

    class Meta:
        db_table = 't_module'


# 角色表
class Role(models.Model):
    roleName = models.CharField(max_length=20, db_column='role_name')
    roleRemark = models.CharField(max_length=120, db_column='role_remark')
    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date', auto_now_add=True)
    updateDate = models.DateTimeField(max_length=20, db_column='update_date',
                                      auto_now_add=True)
    permissions = models.ManyToManyField(Module, through="Permission", through_fields=('role', 'module'))
    objects = ModelManager()

    class Meta:
        db_table = 't_role'


# 角色-资源中间表
class Permission(models.Model):
    role = models.ForeignKey(Role, db_column='role_id', db_constraint=False,
                             on_delete=models.DO_NOTHING)
    module = models.ForeignKey(Module, db_column='module_id', db_constraint=False,
                               on_delete=models.DO_NOTHING)
    aclValue = models.CharField(max_length=20, db_column='acl_value')
    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date', auto_now_add=True)
    updateDate = models.DateTimeField(max_length=20, db_column='update_date',
                                      auto_now_add=True)
    objects = ModelManager()

    class Meta:
        db_table = 't_permission'


# 用户-角色中间表
class UserRole(models.Model):
    user = models.ForeignKey(TUser, db_column='user_id',
                             db_constraint=False, on_delete=models.DO_NOTHING)
    role = models.ForeignKey(Role, db_column='role_id',
                             db_constraint=False, on_delete=models.DO_NOTHING)
    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date', auto_now_add=True)
    updateDate = models.DateTimeField(max_length=20, db_column='update_date',
                                      auto_now_add=True)
    objects = ModelManager()

    class Meta:
        db_table = 't_user_role'
