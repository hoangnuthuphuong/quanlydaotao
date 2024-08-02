from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_training_data, name='index'),
    path('search/', views.search_data, name='search'),
    path('edit/<int:ID>/', views.edit_data, name='edit_data'),
    path('add/', views.add_employee, name='add_employee'),  # Thêm thủ công
    path('upload/', views.upload_excel, name='upload_excel'),  # Thêm bằng Excel
    # path('login/', views.login, name='login'),
]

