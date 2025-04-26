from django.urls import path
from . import views

urlpatterns = [
    path('material-issue/', views.material_issue, name='material_issue'),
    path('material-issue/add/', views.material_issue_add, name='material_issue_add'),
    path('material-issue/edit/', views.material_issue_edit, name='material_issue_edit'),
    path('material-issue/delete/', views.material_issue_delete, name='material_issue_delete'),
    path('get-mr-items/', views.get_mr_items, name='get_mr_items'),
    path('get-warehouse-stock/', views.get_warehouse_stock, name='get_warehouse_stock'),
] 