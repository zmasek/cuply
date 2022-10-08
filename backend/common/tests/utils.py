from django.urls import reverse

def auth_user(client, user):
    result = client.post(
        reverse("token_obtain_pair"),
        data={
            "username": user.username,
            "password": "password",
        },
    )

    access = result.data["access"]
    refresh = result.data["refresh"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
