from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('assets/', views.asset_report, name='asset_report'),
    path('depreciation/', views.depreciation_report, name='depreciation_report'),
    path('transfers/', views.transfer_report, name='transfer_report'),
    path('disposals/', views.disposal_report, name='disposal_report'),
    path('acquisitions/', views.acquisition_report, name='acquisition_report'),
]
