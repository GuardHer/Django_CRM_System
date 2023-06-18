from datetime import datetime

from django.shortcuts import render
import pymysql
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from customer.models import Customer, LinkMan
from sales.models import SaleChance, CusDevPlan
from system.models import TUser


@xframe_options_exempt
@require_GET
def sales_index(request):
    """跳转营销管理首页"""
    return render(request, 'sales/sale_chance.html')


@require_GET
def select_sale_chance_list(request):
    try:
        page_num = request.GET.get('page')  # 页号
        page_size = request.GET.get('limit')  # 页容量

        state = request.GET.get('state')
        # 客户名称
        customerName = request.GET.get('customerName')
        # 创建人
        createMan = request.GET.get('createMan')
        # 开发状态（客户开发计划使用）
        devResult = request.GET.get('devResult')

        if customerName:
            users = SaleChance.objects.filter(isValid=1, customerName=customerName).values()
        elif createMan:
            users = SaleChance.objects.filter(isValid=1, createMan=createMan).values()
        elif state:
            users = SaleChance.objects.filter(isValid=1, state=state).values()
        elif devResult:
            users = SaleChance.objects.filter(isValid=1, devResult=devResult).values()
        else:
            users = SaleChance.objects.filter(isValid=1).values()

        paginator = Paginator(users, page_size)
        users_list = paginator.page(page_num).object_list

        context = {
            'code': 0,
            'msg': '',
            'count': len(users),
            'data': list(users_list)
        }

        return JsonResponse(context)

    except Exception as e:
        return JsonResponse({'code': 400, 'msg': 'error'})


@xframe_options_exempt
@require_GET
def create_or_update_sales(request):
    """跳转添加/修改营销机会页面"""
    # 获取营销机会主键
    saleChanceId = request.GET.get('saleChanceId')
    context = None
    if saleChanceId:
        # 根据营销机会主键查询
        sc = SaleChance.objects.get(pk=saleChanceId)
        context = {'sc': sc}
    return render(request, 'sales/add_update.html', context)


@require_GET
def select_customer(request):
    """查询客户"""
    customer = Customer.objects.values("id", 'name') \
        .filter(isValid=1).order_by('-id').all()
    return JsonResponse(list(customer), safe=False)


@csrf_exempt
@require_GET
def create_sale_chance(request):
    """添加营销机会和联系人"""
    try:
        # 接收参数
        customerId = request.GET.get('customer')
        customerName = request.GET.get('customerName')
        chanceSource = request.GET.get('chanceSource')
        linkMan = request.GET.get('linkMan')
        linkPhone = request.GET.get('linkPhone')
        cgjl = request.GET.get('cgjl')
        overview = request.GET.get('overview')
        description = request.GET.get('description')
        assignMan = request.GET.get('assignMan')
        # 如果有联系人还要添加联系人表数据
        if linkMan:
            lm = LinkMan(cusId=customerId, linkName=linkMan, phone=linkPhone)
            lm.save()
        # 如果有分配人，添加分配时间，分配状态为已分配
        if assignMan != '0':
            sc = SaleChance(customerId=customerId, customerName=customerName,
                            chanceSource=chanceSource, linkMan=linkMan,
                            linkPhone=linkPhone,
                            cgjl=cgjl, overview=overview, description=description,
                            assignMan=assignMan, assignTime=datetime.now(), state=1,
                            devResult=0,
                            createMan=request.session.get('user')['username'])
        else:
            sc = SaleChance(customerId=customerId, customerName=customerName,
                            chanceSource=chanceSource, linkMan=linkMan,
                            linkPhone=linkPhone,
                            cgjl=cgjl, overview=overview, description=description,
                            state=0, devResult=0,
                            createMan=request.session.get('user')['username'])
        # 插入数据
        sc.save()
        # 返回提示信息
        return JsonResponse({'code': 200, 'msg': '添加成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '添加失败'})


@csrf_exempt
@require_GET
def update_sale_chance(request):
    """修改营销机会和联系人"""
    try:
        # 接收参数
        id = request.GET.get('id')
        customerId = request.GET.get('customer')
        customerName = request.GET.get('customerName')
        chanceSource = request.GET.get('chanceSource')
        linkMan = request.GET.get('linkMan')
        linkPhone = request.GET.get('linkPhone')
        cgjl = request.GET.get('cgjl')
        overview = request.GET.get('overview')
        description = request.GET.get('description')
        assignMan = request.GET.get('assignMan')
        # 根据主键查询营销机会
        sc = SaleChance.objects.get(pk=id)
        # 如果有联系人还要修改联系人表数据
        if linkMan != sc.linkMan:
            LinkMan.objects.filter(cusId=customerId) \
                .update(linkName=linkMan, phone=linkPhone, updateDate=datetime.now())
        # 如果用户取消了分配人，要改变分配状态为未分配
        if assignMan == '0':
            sc.state = 0
            sc.assignMan = None
            sc.assignTime = None
        else:
            sc.state = 1
            sc.assignMan = assignMan
            sc.assignTime = datetime.now()
        # 重新赋值
        sc.customerId = customerId
        sc.customerName = customerName
        sc.chanceSource = chanceSource
        sc.linkMan = linkMan
        sc.linkPhone = linkPhone
        sc.cgjl = cgjl
        sc.overview = overview
        sc.description = description
        sc.updateDate = datetime.now()
        # 保存
        sc.save()
        # 返回提示信息
        return JsonResponse({'code': 200, 'msg': '修改成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '修改失败'})


@csrf_exempt
@require_GET
def delete_sale_chance(request):
    """删除营销机会"""
    try:
        # 接收参数
        ids = request.GET.get('ids')
        id_list = list(map(int, ids.split(",")))
        SaleChance.objects.filter(pk__in=id_list).delete()

        return JsonResponse({'code': 200, 'msg': '删除成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '删除失败'})


@xframe_options_exempt
@require_GET
def cus_dev_plan_index(request):
    """跳转营销机会管理首页"""
    return render(request, 'sales/cus_dev_plan.html')


@xframe_options_exempt
@require_GET
def cus_dev_plan_index_detail(request):
    """跳转客户开发计划详情页"""
    # 接收参数
    saleChanceId = request.GET.get('saleChanceId')
    # 根据主键查询营销机会
    sc = SaleChance.objects.get(pk=saleChanceId)
    context = {'sc': sc}
    return render(request, 'sales/cus_dev_plan_detail.html', context)


@require_GET
def select_cus_dev_plan_list(request):
    """查询客户开发计划详细列表"""
    try:
        # 获取第几页
        page_num = request.GET.get('page', 1)
        # 获取每页多少条
        page_size = request.GET.get('limit', 10)
        # 获取客户营销机会主键
        saleChanceId = request.GET.get('saleChanceId')
        # 查询
        cdp_list = CusDevPlan.objects.extra(select={'planDate': 'date_format(plan_date, "%%Y-%%m-%%d")'}) \
            .values('id', 'planItem', 'planDate', 'exeAffect', 'saleChance') \
            .filter(saleChance=saleChanceId).order_by('-id')
        # 初始化分页对象
        p = Paginator(cdp_list, page_size)
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
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': 'error'})


@xframe_options_exempt
@require_GET
def create_or_update_cus_dev_plan(request):
    """跳转客户开发计划添加/修改页面"""
    # 获取营销机会主键
    saleChanceId = request.GET.get('saleChanceId')
    # 获取客户开发计划主键
    id = request.GET.get('id')
    context = {'saleChanceId': saleChanceId}
    if id:
        cusDevPlan = CusDevPlan.objects.get(pk=id)
        context['cusDevPlan'] = cusDevPlan
    return render(request, 'sales/cus_dev_plan_add_update.html', context)


@csrf_exempt
@require_GET
def create_cus_dev_plan(request):
    """添加客户开发计划"""
    # 接收参数
    data = request.GET.dict()
    # 弹出营销机会主键
    saleChanceId = data.pop('saleChanceId')
    # 删除主键
    del data['id']
    # 获取营销机会对象
    sc = SaleChance.objects.get(pk=saleChanceId)
    data['saleChance'] = sc
    # 添加客户开发计划
    CusDevPlan.objects.create(**data)
    # 修改营销机会的开发状态为开发中
    sc.devResult = 1
    sc.updateDate = datetime.now()
    sc.save()
    return JsonResponse({'code': 200, 'msg': '添加成功'})


@csrf_exempt
@require_GET
def update_cus_dev_plan(request):
    """修改客户开发计划"""
    # 接收参数
    data = request.GET.dict()
    # 弹出营销机会主键
    saleChanceId = data.pop('saleChanceId')
    # 删除主键
    id = data.pop('id')
    # 修改时间
    data['updateDate'] = datetime.now()
    # 修改客户开发计划
    CusDevPlan.objects.filter(pk=id).update(**data)
    return JsonResponse({'code': 200, 'msg': '修改成功'})


@csrf_exempt
@require_GET
def delete_cus_dev_plan(request):
    """删除客户开发计划"""
    # 获取主键
    id = request.GET.get('id')
    # 逻辑删除客户开发计划
    CusDevPlan.objects.filter(pk=id).update(isValid=0, updateDate=datetime.now())
    return JsonResponse({'code': 200, 'msg': '删除成功'})


@csrf_exempt
@require_GET
def update_dev_result(request):
    """开发成功或者开发失败"""
    # 接收参数
    saleChanceId = request.GET.get('saleChanceId')
    devResult = request.GET.get('devResult')
    SaleChance.objects.filter(pk=saleChanceId).update(devResult=devResult,
                                                      updateDate=datetime.now())
    return JsonResponse({'code': 200, 'msg': '操作成功'})
