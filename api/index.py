import os
import sys
from django.core.wsgi import get_wsgi_application

# Tambahkan root direktori ke sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Gunakan 'core.settings', BUKAN 'b2b_dashboard.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = get_wsgi_application()