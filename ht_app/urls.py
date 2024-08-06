from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_training_data, name='index'),
    path('dailyreport/', views.dailyreport, name='dailyreport'),
    path('weekreport/', views.dailyreport, name='weekreport'),
    path('search/', views.search_data, name='search'),
    path('search_danhsach_nv_ajax/', views.search_danhsach_nv_ajax, name='search_nv'),
    path('edit_employee_data/<int:ID>/', views.edit_employee_data, name='edit_employee_data'),
    path('edit_dailyreport_data/<int:ID>/<str:Date>/', views.edit_dailyreport_data, name='edit_dailyreport_data'),
    path('add/', views.add_employee, name='add_employee'),  # Thêm thủ công
    path('upload/', views.upload_excel, name='upload_excel'),  # Thêm bằng Excel
    path('download/', views.export_to_excel, name='export_to_excel'),
    # path('uploadLC/', views.upload_LC, name='uploadLC'),
    # path('login/', views.login, name='login'),
]

