from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    # Asset management
    path('', views.asset_list, name='asset_list'),
    path('create/', views.asset_create, name='asset_create'),
    path('<int:pk>/', views.asset_detail, name='asset_detail'),
    path('<int:pk>/update/', views.asset_update, name='asset_update'),
    path('<int:pk>/delete/', views.asset_delete, name='asset_delete'), # Re-enabled after view check
    
    # Excel import
    path('import-excel/', views.import_excel, name='import_excel'),
    path('import-excel/mapping/', views.import_excel_mapping, name='import_excel_mapping'),
    path('import-excel/preview/', views.import_excel_preview, name='import_excel_preview'),
    
    # Depreciation
    path('depreciation/', views.depreciation_management, name='depreciation_management'),
    path('depreciation/calculate/', views.calculate_depreciation, name='calculate_depreciation'),
    path('depreciation/post/', views.post_depreciation, name='post_depreciation'),
    
    # Transfers
    path('transfers/', views.transfer_list, name='transfer_list'),
    path('transfers/create/', views.transfer_create, name='transfer_create'), # Placeholder view exists
    path('transfers/<int:pk>/', views.transfer_detail, name='transfer_detail'), # Placeholder view exists
    # path('transfers/<int:pk>/update/', views.transfer_update, name='transfer_update'), # Commented out - view not implemented
    # path('transfers/<int:pk>/delete/', views.transfer_delete, name='transfer_delete'), # Commented out - view not implemented
    
    # Disposals
    path('disposals/', views.disposal_list, name='disposal_list'),
    path('disposals/create/', views.disposal_create, name='disposal_create'), # Placeholder view exists
    path('disposals/<int:pk>/', views.disposal_detail, name='disposal_detail'), # Placeholder view exists
    # path('disposals/<int:pk>/update/', views.disposal_update, name='disposal_update'), # Commented out - view not implemented
    # path('disposals/<int:pk>/delete/', views.disposal_delete, name='disposal_delete'), # Commented out - view not implemented

    # HTMX Helper
    path('load-subcategories/', views.load_subcategories, name='load_subcategories'),
]

