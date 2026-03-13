import firebase_admin
from firebase_admin import credentials, firestore
import os

# Get the absolute path to serviceAccountKey.json
base_dir = os.path.dirname(os.path.abspath(__file__))
service_account_path = os.path.join(base_dir, '..', 'serviceAccountKey.json')

# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()