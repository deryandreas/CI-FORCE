from django.shortcuts import render, redirect
from datetime import datetime, timedelta
import math
from .models import BatchInhibitor, WarehouseSetting
from .services import get_iqair_weather

def get_active_warehouse():
    """Mengambil atau membuat entri pengaturan gudang pertama jika belum ada."""
    warehouse = WarehouseSetting.objects.first()
    if not warehouse:
        warehouse = WarehouseSetting.objects.create(
            nama_gudang='Gudang Depok',
            alamat='Jl. Leksono, RT.003/RW.004, Brajan, Jlamprang, Kec. Leksono, Kabupaten Wonosobo, Jawa Tengah 56362',
            latitude=-7.3614,
            longitude=109.9004,
            stasiun_bmkg='BMKG Stasiun Wonosobo'
        )
    return warehouse

def dashboard_home(request):
    weather = get_iqair_weather()
    batches = BatchInhibitor.objects.all().order_by('-created_at')
    total_batch = batches.count()
    
    terlindungi_count = 0
    butuh_pelapisan_count = 0
    
    for b in batches:
        if b.masa_aman_hari <= 2:
            butuh_pelapisan_count += 1
        elif b.masa_aman_hari > 2:
            terlindungi_count += 1

    persen_terlindungi = round((terlindungi_count / total_batch * 100), 1) if total_batch > 0 else 0
    persen_butuh = round((butuh_pelapisan_count / total_batch * 100), 1) if total_batch > 0 else 0

    stats = {
        'total_batch': f"{total_batch:,}",
        'terlindungi': f"{terlindungi_count:,}",
        'persen_terlindungi': f"{persen_terlindungi}%",
        'butuh_pelapisan': f"{butuh_pelapisan_count:,}",
        'persen_butuh': f"{persen_butuh}%",
        'efisiensi': '80.01%',
    }

    recent_activities = []
    for b in batches[:5]:
        recent_activities.append({
            'title': f"Batch {b.id_batch} berhasil dibuat",
            'desc': f"{b.jumlah} pcs plat {b.jenis_material} dilindungi dosis {b.dosis_rekomendasi} di {b.lokasi_gudang}",
            'time': b.created_at.strftime("%d %b %Y, %H:%M WIB"),
            'is_warning': False
        })
        if b.masa_aman_hari <= 2:
            recent_activities.append({
                'title': f"⚠️ Peringatan: Batch {b.id_batch}",
                'desc': f"Masa aman perlindungan di {b.lokasi_gudang} tersisa {b.masa_aman_hari} hari",
                'time': "Perlu tindakan",
                'is_warning': True
            })

    context = {
        'page_title': 'Ringkasan Eksekutif',
        'warehouse_status': weather,
        'stats': stats,
        'recent_activities': recent_activities,
    }
    return render(request, 'dashboard/pages/ringkasan.html', context)

def kalkulator_page(request):
    weather = get_iqair_weather()
    warehouse = get_active_warehouse()
    hasil = None
    inputs = {}

    if request.method == "POST":
        action = request.POST.get('action')
        
        jenis_material = request.POST.get('jenis_material', 'ST-37')
        ketebalan_raw = request.POST.get('ketebalan', '').strip()
        panjang_raw = request.POST.get('panjang', '').strip()
        lebar_raw = request.POST.get('lebar', '').strip()
        jumlah_raw = request.POST.get('jumlah', '').strip()
        kelembapan_raw = request.POST.get('kelembapan', '').strip()
        suhu_raw = request.POST.get('suhu', '').strip()

        inputs = {
            'jenis_material': jenis_material,
            'ketebalan': ketebalan_raw if ketebalan_raw else '',
            'panjang': panjang_raw,
            'lebar': lebar_raw,
            'jumlah': jumlah_raw,
            'kelembapan': kelembapan_raw,
            'suhu': suhu_raw,
        }

        if panjang_raw and lebar_raw and jumlah_raw and kelembapan_raw:
            try:
                panjang = float(panjang_raw)
                lebar = float(lebar_raw)
                jumlah = int(jumlah_raw)
                kelembapan_user = float(kelembapan_raw)

                # Formula 1: V_total
                A_cm2 = 2.0 * (panjang * lebar) * jumlah
                total_area_m2 = A_cm2 / 10000.0
                delta = 0.01
                v_total = (A_cm2 * delta) / 1000.0

                # Formula 2: T
                cr_base = 0.000278607
                if kelembapan_user > 75:
                    risk_factor = 1.0 + ((kelembapan_user - 75) / 100.0)
                    cr_actual = cr_base * risk_factor
                else:
                    cr_actual = cr_base

                toleransi_per_cm2 = 0.0039
                delta_w_allowable = toleransi_per_cm2 * A_cm2
                t_days = math.floor(delta_w_allowable / (cr_actual * A_cm2))
                t_days = max(1, t_days)

                target_date = datetime.now() + timedelta(days=t_days)
                tanggal_kadaluarsa = target_date.strftime('%d/%m/%Y')
                dosis_rekomendasi = "10% CF3" if kelembapan_user > 75 else "7% CF3"

                # Simpan batch ke DB dengan lokasi nama gudang aktif
                if action == "save_batch":
                    batch_id = f"BTC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                    
                    BatchInhibitor.objects.create(
                        id_batch=batch_id,
                        jenis_material=jenis_material,
                        ketebalan=float(ketebalan_raw) if ketebalan_raw else None,
                        panjang=panjang,
                        lebar=lebar,
                        jumlah=jumlah,
                        total_area_m2=round(total_area_m2, 4),
                        volume_larutan=round(v_total, 4),
                        masa_aman_hari=t_days,
                        tanggal_kadaluarsa=tanggal_kadaluarsa,
                        dosis_rekomendasi=dosis_rekomendasi,
                        lokasi_gudang=warehouse.nama_gudang
                    )
                    return redirect('riwayat_batch')

                if v_total < 0.01:
                    volume_display = f"{v_total * 1000:.2f} mL"
                else:
                    volume_display = f"{v_total:,.2f} L"

                if total_area_m2 < 0.01:
                    area_display = f"{total_area_m2:,.4f}"
                else:
                    area_display = f"{total_area_m2:,.2f}"

                hasil = {
                    'total_area': area_display,
                    'volume_larutan': volume_display,
                    'masa_aman': f"{t_days} Hari",
                    'tanggal_kadaluarsa': tanggal_kadaluarsa,
                    'dosis_rekomendasi': dosis_rekomendasi,
                    'is_high_risk': kelembapan_user > 75,
                }
            except (ValueError, ZeroDivisionError):
                pass

    context = {
        'page_title': 'Kalkulator Prediktif',
        'warehouse_status': weather,
        'hasil': hasil,
        'inputs': inputs,
    }
    return render(request, 'dashboard/pages/kalkulator.html', context)

def riwayat_batch_page(request):
    weather = get_iqair_weather()
    batches = BatchInhibitor.objects.all().order_by('-created_at')
    
    total_batch = batches.count()
    terlindungi_count = 0
    butuh_pelapisan_count = 0
    kadaluarsa_count = 0
    
    processed_batches = []
    
    for b in batches:
        if b.masa_aman_hari <= 0:
            status = "Kadaluarsa"
            sisa_hari_str = "Expired"
            kadaluarsa_count += 1
        elif b.masa_aman_hari <= 2:
            status = "Butuh Pelapisan"
            sisa_hari_str = f"{b.masa_aman_hari} hari"
            butuh_pelapisan_count += 1
        else:
            status = "Terlindungi"
            sisa_hari_str = f"{b.masa_aman_hari} hari"
            terlindungi_count += 1

        if b.volume_larutan < 0.01:
            vol_str = f"{b.volume_larutan * 1000:.2f} mL"
        else:
            vol_str = f"{b.volume_larutan:.2f} L"

        processed_batches.append({
            'id': b.id_batch,
            'material': f"Plat {b.jenis_material}",
            'dimensi': f"{b.panjang} x {b.lebar} cm",
            'qty': b.jumlah,
            'dosis': b.dosis_rekomendasi,
            'status': status,
            'sisa_hari': sisa_hari_str,
            'lokasi': f"{b.lokasi_gudang} (Vol: {vol_str})"
        })

    quick_stats = {
        'total': total_batch,
        'terlindungi': terlindungi_count,
        'butuh_pelapisan': butuh_pelapisan_count,
        'kadaluarsa': kadaluarsa_count,
    }

    context = {
        'page_title': 'Riwayat Batch',
        'warehouse_status': weather,
        'quick_stats': quick_stats,
        'batch_list': processed_batches,
    }
    return render(request, 'dashboard/riwayat_batch.html', context)

def laporan_esg_page(request):
    weather = get_iqair_weather()
    context = {
        'page_title': 'Laporan ESG',
        'warehouse_status': weather,
        'kelompok_tani': [
            {'nama': 'Kelompok Tani Kejajar 1', 'lokasi': 'Wonosobo', 'anggota': 24, 'kontribusi': '1.2 ton'},
            {'nama': 'Kelompok Tani Kejajar 2', 'lokasi': 'Wonosobo', 'anggota': 18, 'kontribusi': '0.9 ton'},
            {'nama': 'Kelompok Tani Kejajar 3', 'lokasi': 'Wonosobo', 'anggota': 32, 'kontribusi': '1.6 ton'},
            {'nama': 'Kelompok Tani Garung', 'lokasi': 'Wonosobo', 'anggota': 15, 'kontribusi': '0.7 ton'},
        ]
    }
    return render(request, 'dashboard/pages/laporan_esg.html', context)

def pengaturan_page(request):
    weather = get_iqair_weather()
    warehouse = get_active_warehouse()
    active_tab = request.GET.get('tab', 'profil')
    
    if request.method == "POST" and request.POST.get('action') == "save_location":
        nama_gudang_input = request.POST.get('nama_gudang', '').strip()
        alamat_input = request.POST.get('alamat', '').strip()
        lat_raw = request.POST.get('latitude', '').strip()
        lon_raw = request.POST.get('longitude', '').strip()
        stasiun_bmkg_input = request.POST.get('stasiun_bmkg', '').strip()

        if nama_gudang_input:
            warehouse.nama_gudang = nama_gudang_input
        if alamat_input:
            warehouse.alamat = alamat_input
        if lat_raw:
            try:
                warehouse.latitude = float(lat_raw)
            except ValueError:
                pass
        if lon_raw:
            try:
                warehouse.longitude = float(lon_raw)
            except ValueError:
                pass
        if stasiun_bmkg_input:
            warehouse.stasiun_bmkg = stasiun_bmkg_input
            
        warehouse.save()
        return redirect('/pengaturan/?tab=lokasi')
        
    allowed_tabs = ['profil', 'lokasi', 'notifikasi', 'api', 'keamanan']
    if active_tab not in allowed_tabs:
        active_tab = 'profil'
        
    context = {
        'page_title': 'Pengaturan',
        'warehouse_status': weather,
        'active_tab': active_tab,
    }
    return render(request, 'dashboard/pages/pengaturan.html', context)