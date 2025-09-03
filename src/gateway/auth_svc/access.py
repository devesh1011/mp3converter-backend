import os
import requests


def login(request):
    auth = request.authorization

    if not auth:
        return None, ("missing credentials", 401)

    basic_auth = (auth.username, auth.password)

    try:
        response = requests.post(
            f"http://{os.getenv('AUTH_SVC_ADDR')}/login", auth=basic_auth, timeout=3
        )
    except requests.exceptions.RequestException:
        return None, ("auth service unavailable", 503)

    if response.status_code == 200:
        return response.json(), None
    else:
        return
