import os
import sys

grotto_location = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(grotto_location, 'lib'))
sys.path.insert(0, os.path.join(grotto_location, 'templates'))
sys.path.insert(0, os.path.join(grotto_location, 'grotto.wsgi'))
sys.path.insert(0, grotto_location)

from app import app as application
