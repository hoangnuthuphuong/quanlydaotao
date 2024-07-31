from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    # path('search/', views.search, name='search'),
    # path('add/', views.add_employee, name='add_employee'),
    # path('edit/<str:employee_id>/', views.edit_employee, name='edit_employee'),
    # path('login/', views.login, name='login'),
    path('', views.display_training_data, name='index'),
    path('search/', views.search_data, name='search'),
    path('edit/', views.edit_data, name='edit_data'),
]

