from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('kalkulator/', views.kalkulator_page, name='kalkulator'), # <-- Tambahkan baris ini
    path('riwayat-batch/', views.riwayat_batch_page, name='riwayat_batch'), # <-- Tambahkan baris ini
    path('laporan-esg/', views.laporan_esg_page, name='laporan_esg'), # <-- Tambahkan baris ini
    path('pengaturan/', views.pengaturan_page, name='pengaturan'), # <-- Tambahkan baris ini
]