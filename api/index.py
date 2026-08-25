import os
import sys

# Tambahkan path root folder dan folder core
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)
sys.path.insert(0, os.path.join(base_dir, 'core'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

from core.wsgi import application

app = application