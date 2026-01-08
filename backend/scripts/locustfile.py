from locust import HttpUser, task, between
import os
import threading

class VMSLoadTester(HttpUser):
    # Shared token across users in the same locust worker process.
    # You can set LOCUST_TOKEN env var to a pre-generated JWT to entirely avoid login requests.
    token = os.getenv("LOCUST_TOKEN", None)
    _token_lock = threading.Lock()

    wait_time = between(1, 5)

    def on_start(self):
        # If a token isn't provided by env, ensure only one login attempt per worker process
        if not VMSLoadTester.token:
            with VMSLoadTester._token_lock:
                if not VMSLoadTester.token:
                    response = self.client.post("/api/auth/login/", json={
                        "email": "admin@gt.com",
                        "password": "AdminPassword123!"
                    })
                    if response.status_code == 200:
                        VMSLoadTester.token = response.json().get("access")
                    else:
                        print(f"Falha no Login (shared): {response.status_code}")
        if VMSLoadTester.token:
            self.headers = {"Authorization": f"Bearer {VMSLoadTester.token}"}
        else:
            # keep headers empty so requests will fail fast and show error
            self.headers = {}

    @task(3)
    def dashboard_load(self):
        if self.headers:
            self.client.get("/api/dashboard/stats/", headers=self.headers, name="/api/dashboard/stats/")
            self.client.get("/api/cameras/", headers=self.headers, name="/api/cameras/")

    @task(1)
    def detections_search(self):
        if self.headers:
            self.client.get("/api/detections/?limit=20", headers=self.headers, name="/api/detections/")

    @task(1)
    def polling_notifications(self):
        if self.headers:
            self.client.get("/api/support/chat/", headers=self.headers, name="/api/support/chat/")