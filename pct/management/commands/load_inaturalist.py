import requests
import urllib.parse
import dateutil.parser
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ...models import iNaturalistObservation
from django.contrib.gis.geos import Point


class Command(BaseCommand):
    help = "fetch observations from iNaturalist.org"

    def handle(self, *args, **options):
        inat = self.authenticated_session()
        query = urllib.parse.urlencode(
            {
                "user_login": settings.INATURALIST["username"],
                "order": "asc",
                "order_by": "id",
                "identified": "true",
                "quality_grade": "casual,research",
            }
        )
        response = inat.get(f"https://api.inaturalist.org/v1/observations?" + query)
        observations = response.json()

        # FIXME: if observations['total_results'] > observations['per_age'], we should paginate.
        # OTOH, per_age defaults to 30 and I plan to run this hourly, so the chances of that
        # happening are super-small. If it does, they'll get picked up next time I think.
        for o in observations["results"]:
            ino, created = iNaturalistObservation.objects.update_or_create(
                inaturalist_id=o["id"],
                defaults=dict(
                    timestamp=dateutil.parser.parse(o["time_observed_at"]),
                    point=Point(*map(float, o["geojson"]["coordinates"])),
                    name=o["taxon"]["preferred_common_name"],
                    url=o["uri"],
                    thumbnail_url=o["photos"][0]["url"],
                    raw=o,
                ),
            )
            self.stdout.write(self.style.SUCCESS(ino.name))

    def authenticated_session(self):
        # The iNat authorization flow is a bit convoluted:
        #
        # 1. oauth authenticate against https://www.inaturalist.org/oauth/token
        #    (I use the password flow, which at least avoids a web-based auth flow)
        # 2. hit https://www.inaturalists.org/users/api_token to exchange the
        #    bearer token for a jwt
        # 3. now you can use this jwt against the API.
        #
        # I guess there's an older API that you only need the bearer token for,
        # but the newer API has a feature that makes my life easy, the id_above
        # search, which takes all the pain out of paginating.

        # 1. Oauth authentication:
        oauth_creds = dict(settings.INATURALIST, grant_type="password")
        oauth_response = requests.post(
            "https://www.inaturalist.org/oauth/token", oauth_creds
        )
        if oauth_response.status_code != 200:
            raise CommandError(
                f"Error getting oauth token from iNat (HTTP {oauth_response.status_code})"
            )

        # 2. get JWT token
        bearer_token = "Bearer " + oauth_response.json()["access_token"]
        jwt_response = requests.get(
            "https://www.inaturalist.org/users/api_token",
            headers={"Authorization": bearer_token},
        )
        if jwt_response.status_code != 200:
            raise CommandError(
                f"Error getting jwt token from iNat (HTTP {jwt_response.status_code})"
            )

        # Make this into a requests.Session with apropriate auth
        s = requests.Session()
        s.headers["Authorization"] = jwt_response.json()["api_token"]
        return s


"""
import requests
payload = {
'client_id': '595657b119b63ac1c0ade0d0e91019111ecb0fea81cb5ff7ae77197ad802210f',
'client_secret': '065fd0b6a7936f4cc7cc81c89f849eb1161f0f56ff917d125aef39e884400fae',
'grant_type': 'password',
'username': 'jacobkm',
'password': 'LrP3vgQUwEfJLdzz'}
resp = requests.post('https://www.inaturalist.org/oauth/token', payload)
resp
resp.json()
headers = {'Authorization': 'Bearer ' + resp.json()['access_token']}
requests.get('https://api.inaturalist.org/v1/users/me', headers=headers)
requests.get('https://www.inaturalists.org/users/api_token', headers=headers)
requests.get('https://www.inaturalist.org/users/api_token', headers=headers)
_.json()
jwt = _['api_token']
requests.get('https://www.inaturalist.org/observations.json', headers=headers)
_.json()
jwt
history
headers2 = {'Authorization': jwt}
requests.get('https://api.inaturalist.org/v1/observations?user_login=jacobkm&order=desc&order_by=created_at', headers=headers2)
_.json()["total_results"]
history
"""
