import requests

url = "http://127.0.0.1:8000/api/admin/mobile-session/create"
res = requests.post(url, headers={"Authorization": "Bearer BADTOKEN"})
print("Create (no token):", res.status_code, res.text)
