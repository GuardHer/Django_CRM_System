from django.db import models


# Create your models here.

class ModelManager(models.Manager):
    def get_queryset(self):
        return super(ModelManager, self).get_queryset().filter(isValid=1)


# 营销机会模型
class SaleChance(models.Model):
    # 信息来源
    chanceSource = models.CharField(max_length=300, db_column='chance_source')
    # 客户id
    customerId = models.IntegerField(db_column='customer_id')
    # 客户名称
    customerName = models.CharField(max_length=100, db_column='customer_name')
    # 成功几率
    cgjl = models.IntegerField(db_column='cgjl')
    # 概要
    overview = models.CharField(max_length=300, db_column='overview')
    # 联系人
    linkMan = models.CharField(max_length=20, db_column='link_man')
    # 联系电话
    linkPhone = models.CharField(max_length=20, db_column='link_phone')
    # 描述
    description = models.CharField(max_length=1000, db_column='description')
    # 创建人
    createMan = models.CharField(max_length=20, db_column='create_man')
    # 分配给谁
    assignMan = models.CharField(max_length=20, db_column='assign_man')
    # 分配时间
    assignTime = models.DateTimeField(db_column='assign_time')
    # 状态：1-如果有分配就是已分配状态，0-未分配
    state = models.CharField(max_length=20, db_column='state')
    # 开发状态：0=未开发 1=开发中 2=开完完成 3=开发失败
    devResult = models.CharField(max_length=20, db_column='dev_result')
    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date', auto_now_add=True)
    updateDate = models.DateTimeField(max_length=20, db_column='update_date')
    objects = ModelManager()

    class Meta:
        db_table = 't_sale_chance'


# 客户计划模型
class CusDevPlan(models.Model):
    # 关联营销机会
    saleChance = models.ForeignKey(SaleChance, db_constraint=False,
                                   db_column='sale_chance_id',
                                   on_delete=models.DO_NOTHING)
    # 计划内容
    planItem = models.CharField(max_length=300, db_column='plan_item')
    # 计划时间
    planDate = models.DateTimeField(max_length=20, db_column='plan_date')
    # 执行效果
    exeAffect = models.CharField(max_length=100, db_column='exe_affect')
    isValid = models.IntegerField(db_column='is_valid')
    createDate = models.DateTimeField(db_column='create_date')
    updateDate = models.DateTimeField(max_length=20, db_column='update_date')
    objects = ModelManager()

    class Meta:
        db_table = 't_cus_dev_plan'
