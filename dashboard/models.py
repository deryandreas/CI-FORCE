from django.db import models

class WarehouseSetting(models.Model):
    """
    Menyimpan konfigurasi lokasi gudang yang diisi langsung oleh pengguna.
    """
    nama_gudang = models.CharField(max_length=100)
    alamat = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    stasiun_bmkg = models.CharField(max_length=100, blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nama_gudang


class BatchInhibitor(models.Model):
    """
    Menyimpan data riwayat batch berdasarkan input kalkulasi pengguna.
    """
    id_batch = models.CharField(max_length=50, unique=True)
    jenis_material = models.CharField(max_length=50)
    ketebalan = models.FloatField(null=True, blank=True)
    panjang = models.FloatField()
    lebar = models.FloatField()
    jumlah = models.IntegerField()
    total_area_m2 = models.FloatField()
    volume_larutan = models.FloatField()
    masa_aman_hari = models.IntegerField()
    tanggal_kadaluarsa = models.CharField(max_length=20)
    dosis_rekomendasi = models.CharField(max_length=20)
    lokasi_gudang = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id_batch} - {self.lokasi_gudang}"