from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Case, When, Value
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_GET
from customer.models import Customer
from serve.models import CustomerServe

from customer.views import loss_index, select_loss_list


# Create your views here.

@xframe_options_exempt
@require_GET
def report_index(request, template):
    """统计报表子菜单首页"""
    ''' 
        contribute 客户贡献分析首页 
        composition 客户构成分析首页 
        serve 客户服务分析首页 
        loss 客户流失分析首页 
    '''
    return render(request, 'report/%s.html' % template)


@require_GET
def select_contribute(request):
    """查询客户贡献"""
    try:

        # """
        #     SELECT c.id, c.name, sum(od.sum) sum FROM t_customer c
        #     LEFT JOIN t_customer_order co ON c.id = co.cus_id
        #     LEFT JOIN t_order_details od ON co.id = od.order_id
        #     WHERE c.is_valid = 1 AND c.id = 1 GROUP BY c.id, c.name;
        # """
        # 获取第几页
        page_num = request.GET.get('page', 1)  # 添加默认值，防止没有参数导致的异常错误
        # 获取每页多少条
        page_size = request.GET.get('limit', 10)  # 添加默认值，防止没有参数导致的异常错误
        customer_list = Customer.objects.values('id', 'name') \
            .annotate(sum=Sum('customerorders__ordersdetail__sum')) \
            .order_by('-sum')
        # 按条件查询
        # 客户名称
        customerName = request.GET.get('customerName')
        if customerName:
            customer_list = customer_list.filter(name__icontains=customerName)
        # 金额区间
        type = request.GET.get('type')
        if type == '1':
            customer_list = customer_list.filter(sum__gte=0, sum__lte=1000)
        elif type == '2':
            customer_list = customer_list.filter(sum__gt=1000, sum__lte=3000)
        elif type == '3':
            customer_list = customer_list.filter(sum__gt=3000, sum__lte=5000)
        elif type == '4':
            customer_list = customer_list.filter(sum__gt=5000)
        # 初始化分页对象
        p = Paginator(customer_list, page_size)
        # 获取指定页数的数据
        data = p.page(page_num).object_list
        # 返回总条数
        count = p.count
        # 返回数据，按照 layuimini 要求格式构建
        context = {
            'code': 0,
            'msg': '查询成功',
            'count': count,
            'data': list(data)
        }
        return JsonResponse(context)
    except Exception as e:
        pass


@require_GET
def select_composition(request):
    """查询客户构成数据"""
    level = Customer.objects.values('level') \
        .annotate(amount=Count('level')).order_by('level')
    return JsonResponse(list(level), safe=False)


@require_GET
def select_serve(request):
    """查询客户服务类型数据"""
    serve = CustomerServe.objects.values('serveType') \
        .annotate(type=Case(When(serveType=6, then=Value("咨询")),
                            When(serveType=7, then=Value("建议")),
                            When(serveType=8, then=Value("投诉"))), amount=Count('serveType')) \
        .order_by('serveType')
    return JsonResponse(list(serve), safe=False)



