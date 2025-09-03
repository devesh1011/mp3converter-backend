import os
import requests


def token(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None, ("missing credentials", 401)

    try:
        response = requests.post(
            f"http://{os.getenv('AUTH_SVC_ADDR')}/validate",
            headers={"Authorization": auth_header},
            timeout=3,
        )
    except requests.exceptions.RequestException:
        return None, ("auth service unavailable", 503)

    if response.status_code == 200:
        return response.json(), None
    else:
        return None, (response.text, response.status_code)
