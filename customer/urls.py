from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'customer'

urlpatterns = [
    # 首页
    path('index/', views.customer_index, name='customer_index'),
    path('select_customer_list/', views.select_customer_list, name='select_customer_list'),

    path('create_or_update_customer_page/', views.create_or_update_customer_page, name='create_or_update_customer_page'),
    path('create_or_update_customer/', views.create_or_update_customer, name='create_or_update_customer'),

    path('delete/', views.delete_customer, name='delete_customer'),

    path('order/index/', views.order_index, name='order_index'),
    path('order/list/', views.select_orderlist_by_customerid, name='select_orderlist_by_customerid'),

    path('order/detail/index/', views.order_detail_index, name='order_detail_index'),
    path('order/detail/list/', views.select_orderdetail_by_orderid, name='select_orderdetail_by_orderid'),

    path('loss/index/', views.loss_index, name='loss_index'),
    path('loss/list/', views.select_loss_list, name='select_loss_list'),

    path('loss/detail/index/', views.loss_detail_index, name='loss_detail_index'),
    path('loss/reprieve/list/', views.select_reprieve_by_lossid, name='select_reprieve_by_lossid'),

    path('loss/reprieve/index/', views.reprieve_index, name='reprieve_index'),
    path('loss/reprieve/create/', views.create_reprieve, name='create_reprieve'),
    path('loss/reprieve/update/', views.update_reprieve, name='update_reprieve'),
    path('loss/reprieve/delete/', views.delete_reprieve, name='delete_reprieve'),

    path('loss/confirm/', views.update_lossreason_by_lossid, name='update_lossreason_by_lossid'),
]
