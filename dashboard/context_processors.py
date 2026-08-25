from .models import WarehouseSetting

def warehouse_context(request):
    """
    Mengambil data lokasi gudang yang disimpan pengguna dari database 
    dan menyediakannya secara global ke seluruh file template HTML.
    """
    warehouse = WarehouseSetting.objects.first()
    return {
        'current_warehouse': warehouse
    }