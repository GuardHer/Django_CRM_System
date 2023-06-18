from django.urls import path
from . import views

app_name = 'report'

urlpatterns = [
    path('<str:template>/index/', views.report_index, name='report_index'),
    path('contribute/', views.select_contribute, name='select_contribute'),
    path('composition/', views.select_composition, name='select_composition'),
    path('serve/', views.select_serve, name='select_serve'),

    path('loss/index/', views.loss_index, name='loss_index'),
    path('loss/list/', views.select_loss_list, name='select_loss_list'),
]
