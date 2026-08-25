import os
import sys
from django.core.wsgi import get_wsgi_application

# Tambahkan direktori root ke sys.path agar modul project terbaca oleh Vercel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'b2b_dashboard.settings')

app = get_wsgi_application()