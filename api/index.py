import os
import sys
from django.core.wsgi import get_wsgi_application

# Tambahkan direktori root ke path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Override langsung agar tidak memakai cache environment lama
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

app = get_wsgi_application()