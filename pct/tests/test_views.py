import json
import pathlib
import pytest
from django.conf import settings
from pct import views

HERE = pathlib.Path(__file__).parent
PAYLOAD = open(HERE / "sample-instagram-payload.json").read()


@pytest.mark.django_db
def test_instagram_hook(client):
    response = client.post(
        "/instagram-hook/",
        data=PAYLOAD,
        content_type="application/json",
        HTTP_X_ZAPIER_SECRET=settings.ZAPIER_WEBOOK_SECRET,
    )
    assert response.status_code == 201


def test_instagram_hook_mismatch_secret(client):
    response = client.post(
        "/instagram-hook/",
        data=PAYLOAD,
        content_type="application/json",
        HTTP_X_ZAPIER_SECRET="I'm a little spammer, short and stout",
    )
    assert response.status_code == 400
