from django.urls import path
from . import views

app_name = 'serve'

urlpatterns = [
    path('<str:template>/index/', views.serve_index, name='serve_index'),
    path('list/', views.select_serve_list, name='select_serve_list'),
    path('<str:template>/workflow/', views.serve_workflow, name='serve_workflow'),
    path('create/', views.create_serve, name='create_serve'),
    path('update/', views.update_serve, name='update_serve'),
]
