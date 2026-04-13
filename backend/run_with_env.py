import os

# CRITICAL: Set environment variable BEFORE any app imports
os.environ['ENCRYPTION_KEY'] = 'dev-encryption-key-change-in-production-32bytes'

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("Starting Flask server with ENCRYPTION_KEY set...")
    print(f"ENCRYPTION_KEY: {os.environ.get('ENCRYPTION_KEY')[:20]}...")
    app.run(host='127.0.0.1', port=5000, debug=False)
