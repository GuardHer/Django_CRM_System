from django.urls import path, include
from . import views

app_name = 'sales'
urlpatterns = [
    path('index/', views.sales_index, name='sales_index'),
    path('list/', views.select_sale_chance_list, name='select_sale_chance_list'),

    # 添加/修改营销机会
    path('create_or_update/', views.create_or_update_sales,
         name='create_or_update_sales'),
    path('customer/', views.select_customer, name='select_customer'),
    path('create/', views.create_sale_chance, name='create_sale_chance'),
    path('update/', views.update_sale_chance, name='update_sale_chance'),

    # 删除营销机会
    path('delete/', views.delete_sale_chance, name='delete_sale_chance'),

    path('cus_dev_plan/index/', views.cus_dev_plan_index, name='cus_dev_plan_index'),

    path('cus_dev_plan/detail/', views.cus_dev_plan_index_detail,
         name='cus_dev_plan_index_detail'),
    path('cus_dev_plan/list/', views.select_cus_dev_plan_list,
         name='select_cus_dev_plan_list'),
    
    # 添加/修改/删除开发计划
    path('cus_dev_plan/create_or_update/', views.create_or_update_cus_dev_plan,
         name='create_or_update_cus_dev_plan'),
    path('cus_dev_plan/create/', views.create_cus_dev_plan,
         name='create_cus_dev_plan'),
    path('cus_dev_plan/update/', views.update_cus_dev_plan,
         name='update_cus_dev_plan'),
    path('cus_dev_plan/delete/', views.delete_cus_dev_plan,
         name='delete_cus_dev_plan'),
    
    path('cus_dev_plan/dev_result/', views.update_dev_result,
         name='update_dev_result'),
]
