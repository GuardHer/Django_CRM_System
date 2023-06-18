from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.paginator import Paginator
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from customer.models import Customer, CustomerOrders, OrdersDetail, CustomerLoss, CustomerReprieve


# Create your views here.
@xframe_options_exempt
def customer_index(request):
    return render(request, 'customer/customer.html')


@require_GET
def select_customer_list(request):
    try:
        page_num = request.GET.get('page')  # 页号
        page_size = request.GET.get('limit')  # 页容量

        users = Customer.objects.filter(isValid=1).values()
        paginator = Paginator(users, page_size)
        count = paginator.count
        users_list = paginator.page(page_num).object_list

        user_response = {
            'code': 0,
            'msg': '',
            'count': count,
            'data': list(users_list)
        }

        return JsonResponse(user_response)

    except Exception as e:
        return JsonResponse({'code': 400, 'msg': "error"})


@csrf_exempt
@xframe_options_exempt
def create_or_update_customer_page(request):
    # 获取需要编辑客户的id并发送，修改客户信息时需要使用
    id = request.GET.get('id')
    # 如果查询不到 id 就是添加客户操作，反之就是修改操作
    if id is not None and id != '':
        customer = Customer.objects.values().filter(id=id)  # 根据id查找数据库客户信息
        return render(request, 'customer/customer_add_update.html', customer[0])  # 修改操作，需要发送id，便于修改时定位客户
    else:
        return render(request, 'customer/customer_add_update.html')  # 新建操作，无需id


def create_or_update_customer(request):
    try:  # 接收参数
        name = request.GET.get('name')
        area = request.GET.get('area')
        cusManager = request.GET.get('cusManager')
        level = request.GET.get('level')
        xyd = request.GET.get('xyd')
        postCode = request.GET.get('postCode')
        phone = request.GET.get('phone')
        fax = request.GET.get('fax')
        website = request.GET.get('website')
        address = request.GET.get('address')
        fr = request.GET.get('fr')
        zczj = request.GET.get('zczj')
        nyye = request.GET.get('nyye')
        khyh = request.GET.get('khyh')
        khzh = request.GET.get('khzh')
        dsdjh = request.GET.get('dsdjh')
        gsdjh = request.GET.get('gsdjh')

        id = request.GET.get('id')
        c = None

        # 如果id为空 说明无此用户，故为新建客户操作
        if not id:
            # KH + 时间
            khno = 'KH' + datetime.now().strftime('%Y%m%d%H%M%S')
            # 添加数据
            Customer.objects.create(khno=khno, name=name, area=area,
                                    cusManager=cusManager, level=level,
                                    xyd=xyd, postCode=postCode, phone=phone,
                                    fax=fax, website=website,
                                    address=address, fr=fr, zczj=zczj, nyye=nyye,
                                    khyh=khyh,
                                    khzh=khzh, dsdjh=dsdjh, gsdjh=gsdjh)
        #  如果id有值 说明已经有此用户，故对其进行修改操作
        else:
            # 修改数据
            Customer.objects.filter(id=id).update(name=name, area=area,
                                                  cusManager=cusManager, level=level,
                                                  xyd=xyd, postCode=postCode,
                                                  phone=phone, fax=fax,
                                                  website=website,
                                                  address=address, fr=fr,
                                                  zczj=zczj, nyye=nyye, khyh=khyh,
                                                  khzh=khzh, dsdjh=dsdjh,
                                                  gsdjh=gsdjh,
                                                  updateDate=datetime.now())
        # 返回提示信息
        return JsonResponse({'code': 200, 'msg': '保存成功'})

    except Exception as es:
        return JsonResponse({'code': 400, 'msg': '保存失败'})


@csrf_exempt
@require_GET
def delete_customer(request):
    """根据主键删除客户信息"""
    try:
        # 接收参数
        id = request.GET.get('id')
        # 逻辑删除
        # Customer.objects.filter(pk=id).update(isValid=0, updateDate=datetime.now())
        Customer.objects.get(pk=id).delete()
        return JsonResponse({'code': 200, 'msg': '删除成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '删除失败'})


@xframe_options_exempt
@require_GET
def order_index(request):
    """跳转订单查看页面"""
    # 接收参数
    id = request.GET.get('id')
    # 查询客户信息
    customer = Customer.objects.get(pk=id)
    context = {
        'id': id,
        'khno': customer.khno,
        'name': customer.name,
        'fr': customer.fr,
        'address': customer.address,
        'phone': customer.phone
    }
    return render(request, 'customer/customer_order.html', context)


@xframe_options_exempt
@require_GET
def select_orderlist_by_customerid(request):
    """根据客户主键查询订单"""
    try:
        # 获取第几页
        page_num = request.GET.get('page')
        # 获取每页多少条
        page_size = request.GET.get('limit')
        # 获取客户主键
        id = request.GET.get('id')
        # 查询订单列表
        order_list = CustomerOrders.objects.values().filter(customer=id)
        # 初始化分页对象
        p = Paginator(order_list, page_size)
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
def order_detail_index(request):
    """跳转订单详情页面"""
    # 接收参数
    id = request.GET.get('id')
    # 查询订单信息
    o = CustomerOrders.objects.get(pk=id)
    context = {
        'id': id,
        'orderNo': o.orderNo,
        'totalPrice': o.totalPrice,
        'address': o.address,
        'state': o.get_state_display()
    }
    return render(request, 'customer/customer_order_detail.html', context)


@require_GET
def select_orderdetail_by_orderid(request):
    """根据订单主题查询订单详情"""
    try:
        # 获取第几页
        page_num = request.GET.get('page')
        # 获取每页多少条
        page_size = request.GET.get('limit')
        # 获取订单主键
        id = request.GET.get('id')
        # 查询订单详情
        orderdetail_list = OrdersDetail.objects.values().filter(order=id)
        # 初始化分页对象
        p = Paginator(orderdetail_list, page_size)
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


# def create_customer_loss():
#     """添加暂缓流失客户"""
#     try:
#         # 创建游标对象
#         cursor = connection.cursor()
#         # 编写 SQL
#         sql = '''
#             SELECT
#                 c.id id,
#                 c.khno cusNo,
#                 c.NAME cusName,c.cus_manager cusManager,
#                 max( co.order_date ) lastOrderTime
#             FROM
#                 t_customer c
#                 LEFT JOIN t_customer_order co ON c.id = co.cus_id
#             WHERE
#                 c.is_valid = 1
#                 AND c.state = 0
#                 AND NOW() > DATE_ADD( c.create_date, INTERVAL 6 MONTH )
#                 AND NOT EXISTS (
#                 SELECT DISTINCT
#                 o.cus_id
#                 FROM
#                 t_customer_order o
#                 WHERE
#                 o.is_valid = 1
#                 AND NOW() < DATE_ADD( o.order_date, INTERVAL 6 MONTH )
#                 AND c.id = o.cus_id
#                 )
#             GROUP BY
#                 c.id;
#         '''
#         # 执行sql
#         cursor.execute(sql)
#         # 返回多条结果行
#         customer_loss_tuple = cursor.fetchall()  # 查询当前sql执行后所有的记录，返回元组
#         # 关闭游标
#         cursor.close()
#         # 将元组转为列表
#         customer_loss_id = []  # 暂缓流失客户 id 列表
#         customer_loss_list = []  # 暂缓流失客户列表
#         for cl in customer_loss_tuple:
#             customer_loss_id.append(cl[0])
#             customer_loss_list.append(CustomerLoss(cusNo=cl[1],
#                                                    cusName=cl[2],
#                                                    cusManager=cl[3],
#                                                    lastOrderTime=cl[4],
#                                                    state=0))  # 暂缓流失
#         # 批量插入客户流失表
#         CustomerLoss.objects.bulk_create(customer_loss_list)
#         # 修改这些数据客户表中的状态为 1 暂时流失
#         Customer.objects.filter(id__in=customer_loss_id).update(state=1,
#                                                                 updateDate=datetime.now())
#     except Exception as e:
#         print(e)
#     finally:
#         connection.close()
#
#
# scheduler = BackgroundScheduler()  # 创建一个调度器对象
# scheduler.add_job(create_customer_loss, 'interval', minutes=1)  # 创建一个任务
# scheduler.start()  # 启动任务
@xframe_options_exempt
@require_GET
def loss_index(request):
    return render(request, 'customer/customer_loss.html')


@require_GET
def select_loss_list(request):
    try:
        # 获取第几页
        page_num = request.GET.get('page')
        # 获取每页多少条
        page_size = request.GET.get('limit')
        # 获取客户编号
        cusNo = request.GET.get('cusNo')
        # 获取客户名称
        cusName = request.GET.get('cusName')
        # 获取客户状态
        state = request.GET.get('state')
        # 查询所有
        loss_list = CustomerLoss.objects.values().all().order_by('-lastOrderTime')
        # 如果有条件参数，带条件查询
        if cusNo:
            loss_list = loss_list.filter(cusNo__icontains=cusNo)
        if cusName:
            loss_list = loss_list.filter(cusName__icontains=cusName)
        if state:
            loss_list = loss_list.filter(state=state)
        # 初始化分页对象
        p = Paginator(loss_list, page_size)
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
def loss_detail_index(request):
    try:
        # 获取客户流失主键
        id = request.GET.get('id')
        # 查询客户流失信息
        cl = CustomerLoss.objects.get(pk=id)
        context = {'cl': cl}
        return render(request, 'customer/customer_reprieve.html', context)
    except CustomerLoss.DoesNotExist as e:
        pass


@require_GET
def select_reprieve_by_lossid(request):
    """根据客户流失主键查询流失措施"""
    try:
        page_num = request.GET.get('page')
        page_size = request.GET.get('limit')
        id = request.GET.get('id')

        cp_list = CustomerReprieve.objects.values().filter(customerLoss=id).order_by('-id')

        p = Paginator(cp_list, page_size)

        data = p.page(page_num).object_list

        count = p.count

        context = {'code': 0, 'msg': '', 'count': count, 'data': list(data)}

        return JsonResponse(context)

    except Exception as e:

        return JsonResponse({'code': 400, 'msg': 'error'})


@xframe_options_exempt
@require_GET
def reprieve_index(request):
    """添加客户暂缓页面"""
    lossId = request.GET.get('lossId')
    context = {'lossId': lossId}

    id = request.GET.get('id')

    if id:
        cp = CustomerReprieve.objects.get(pk=id)
        context['id'] = id
        context['cp'] = cp
    return render(request, 'customer/customer_reprieve_add_update.html', context)


@csrf_exempt
@require_GET
def create_reprieve(request):
    """添加客户暂缓"""
    # 获取客户流失主键
    lossId = request.GET.get('lossId')
    # 获取客户暂缓措施
    measure = request.GET.get('measure')
    # 查询流失客户数据
    cl = CustomerLoss.objects.get(pk=lossId)
    data = {
        'customerLoss': cl,
        'measure': measure
    }
    # 添加
    CustomerReprieve.objects.create(**data)
    return JsonResponse({'code': 200, 'msg': '添加成功'})


@csrf_exempt
@require_GET
def update_reprieve(request):
    """修改客户暂缓"""
    # 获取客户暂缓主键
    id = request.GET.get('id')
    # 获取客户暂缓措施
    measure = request.GET.get('measure')
    data = {
        'measure': measure,
        'updateDate': datetime.now()
    }
    # 修改
    CustomerReprieve.objects.filter(pk=id).update(**data)
    return JsonResponse({'code': 200, 'msg': '修改成功'})


@csrf_exempt
@require_GET
def delete_reprieve(request):
    """删除客户暂缓"""
    # 获取客户暂缓主键
    id = request.GET.get('id')
    # 逻辑删除
    CustomerReprieve.objects.filter(pk=id).update(isValid=0,
                                                  updateDate=datetime.now())
    return JsonResponse({'code': 200, 'msg': '删除成功'})


@csrf_exempt
@require_GET
def update_lossreason_by_lossid(request):
    """确认流失"""
    # 获取客户流失主键
    lossId = request.GET.get('lossId')
    # 获取流失原因
    lossReason = request.GET.get('lossReason')
    # 根据客户流失主键查询
    cl = CustomerLoss.objects.get(pk=lossId)
    # 重新赋值
    cl.lossReason = lossReason
    cl.state = 1
    cl.confirmLossTime = datetime.now()
    # 保存
    cl.save()
    # 修改客户表状态
    Customer.objects.filter(khno=cl.cusNo).update(state=2,
                                                  updateDate=datetime.now())
    return JsonResponse({'code': 200, 'msg': '保存成功'})
