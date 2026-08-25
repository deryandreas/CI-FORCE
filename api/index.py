import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)
sys.path.insert(0, os.path.join(base_dir, 'core'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

import django
django.setup()

from django.core.management import call_command
from core.wsgi import application

# Jalankan migrasi otomatis untuk database baru di /tmp
try:
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Migration error: {e}")

app = application