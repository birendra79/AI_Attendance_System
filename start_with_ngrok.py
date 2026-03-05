import os
import sys
import time
import threading
import uvicorn
from pyngrok import ngrok, conf

def start_backend():
    print("Starting FastAPI Backend on port 8000...")
    # Change into the backend folder temporarily just to be safe if .env logic needs it
    os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False) # Reload false in wrapper script

if __name__ == "__main__":
    # If the user has an ngrok authtoken, they should set it in the console before running,
    # or uncomment and place it here: ngrok.set_auth_token("YOUR_TOKEN")

    print("Initializing Ngrok Tunnels...")
    
    # Expose Backend API
    try:
        api_tunnel = ngrok.connect(8000, "http")
        print(f"✅ Backend API Public URL: {api_tunnel.public_url}")
        os.environ["NGROK_BACKEND_URL"] = api_tunnel.public_url
    except Exception as e:
        print(f"Failed to start API Tunnel: {e}")
        sys.exit(1)

    # Expose Frontend Static Server (Assuming 5500 via VS Code Live Server is active)
    # Note: If VS Code Live Server isn't running, this tunnel will just return 502 Bad Gateway
    try:
        frontend_tunnel = ngrok.connect(5500, "http")
        print(f"✅ Frontend Public URL: {frontend_tunnel.public_url}")
        os.environ["NGROK_FRONTEND_URL"] = frontend_tunnel.public_url
    except Exception as e:
        print(f"Failed to start Frontend Tunnel: {e}")

    print("\n" + "="*50)
    print("🌍 GLOBAL MOBILE CAPTURE IS ACTIVE 🌍")
    print("Open the Frontend Public URL on your laptop to start registering users.")
    print("When you scan the QR Code, it will automatically route through these tunnels!")
    print("="*50 + "\n")

    # Start the backend in the main thread (blocking until closed)
    start_backend()
