from datetime import datetime

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from serve.models import CustomerServe


# Create your views here.

@xframe_options_exempt
@require_GET
def serve_index(request, template):
    """跳转服务管理各个功能首页"""
    context = {'username': request.session.get('user')['username']}
    ''' 
        create 创建 assign 分配
        handle 处理
        feedback 反馈 archive 归档 
    '''
    return render(request, 'serve/%s.html' % template, context)


@require_GET
def select_serve_list(request):
    """工作流程中多个页面的公共查询"""
    try:
        # 获取第几页
        page_num = request.GET.get('page', 1)
        # 获取每页多少条
        page_size = request.GET.get('limit', 10)
        # 查询
        select_dict = {
            'assignTime': 'select DATE_FORMAT(assign_time, "%%Y-%%m-%%d-%%H:%%i:%%s")',
            'serviceProceTime': 'select DATE_FORMAT(service_proce_time, "%%Y-%%m-%%d-%%H:%%i:%%s")',
            'createDate': 'select DATE_FORMAT(create_date, "%%Y-%%m-%%d-%%H:%%i:%%s")',
            'updateDate': 'select DATE_FORMAT(update_date, "%%Y-%%m-%%d-%%H:%%i:%%s")',
        }
        queryset = CustomerServe.objects.extra(select=select_dict) \
            .values().order_by('-id').all()
        # 条件查询
        # 服务状态：1 新创建 / 2 已分配 / 3 已处理 / 4 已反馈
        state = request.GET.get('state')
        if state:
            queryset = queryset.filter(state=state)
        # 客户
        customer = request.GET.get('customer')
        if customer:
            queryset = queryset.filter(customer__icontains=customer)
        # 服务类型：6 咨询 / 7 投诉 / 8 建议
        serveType = request.GET.get('serveType')
        if serveType:
            queryset = queryset.filter(serveType=serveType)
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
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': 'error'})


@xframe_options_exempt
@require_GET
def serve_workflow(request, template):
    """工作流程中多个子页面的公共函数"""
    context = {'username': request.session.get('user')['username']}
    # 获取服务主键
    id = request.GET.get('id')
    if id:
        context['cs'] = CustomerServe.objects.get(pk=id)
    return render(request, 'serve/%s_serve.html' % template, context)


@csrf_exempt
@require_GET
def create_serve(request):
    """创建服务"""
    # 接收参数
    data = request.GET.dict()
    # 添加
    CustomerServe.objects.create(**data)
    return JsonResponse({'code': 200, 'msg': '创建成功'})


@csrf_exempt
@require_GET
def update_serve(request):
    """修改服务公共函数"""
    # 接收参数
    serve = request.GET.dict()
    # 弹出主键
    id = serve.pop('id')
    # 获取分配状态
    state = serve.get('state')
    # 如果是 2 已分配，修改分配时间
    if state == '2':
        serve['assignTime'] = datetime.now()
        # 如果是 3 已处理，修改处理时间
    elif state == '3':
        serve['serviceProceTime'] = datetime.now()
        # 当条记录修改时间
    serve['updateDate'] = datetime.now()
    CustomerServe.objects.filter(pk=id).update(**serve)
    return JsonResponse({'code': 200, 'message': '操作成功'})


