import requests
import json
import datetime

API_URL = "https://api.airbnb.com"
# API_KEY might be tied to a particular app installation, use with caution
API_KEY = "915pw2pnf4h1aiguhph5gc5b2"


class AuthError(Exception):
    """
    Authentication error
    """
    pass


class Api(object):
    """ Base API class
    >>> api = Api("vtflotci@sharklasers.com", "qwerty")
    >>> api.uid
    25418725
    >>> api.get_profile() # doctest: +ELLIPSIS
    {...}
    >>> api = Api("foo", "bar") # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    AuthError
    >>> api = Api(uid=25418725, access_token="c9pfdtaakmqh8vrwcyviaai0w")
    """

    def __init__(self, username=None, password=None,
                 uid=None, access_token=None, api_key=API_KEY):
        self._session = requests.Session()

        self._session.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json",
            "X-Airbnb-API-Key": api_key,
            "User-Agent": "Airbnb/4.7.0 iPhone/8.1.2"
        }

        if uid and access_token:
            self.uid = uid
            self._access_token = access_token

            self._session.headers.update({
                "X-Airbnb-OAuth-Token": self._access_token
            })

        else:
            assert(username and password)
            login_payload = {"username": username,
                             "password": password,
                             "prevent_account_creation": "true"}

            r = self._session.post(
                API_URL + "/v1/authorize", data=json.dumps(login_payload)
            )

            if "access_token" not in r.json():
                raise AuthError
            r.raise_for_status()

            self._access_token = r.json()["access_token"]

            self._session.headers.update({
                "X-Airbnb-OAuth-Token": self._access_token
            })

            r = self._session.get(API_URL + "/v1/account/active")

            r.raise_for_status()

            self.uid = r.json()["user"]["user"]["id"]

    def get_profile(self):
        assert(self._access_token and self.uid)

        r = self._session.get(API_URL + "/v1/users/" + str(self.uid))
        r.raise_for_status()

        return r.json()

    def get_listings(self):
        """ Gets listings for uid on api """
        assert(self._access_token and self.uid)

        r = self._session.get(API_URL + "/v1/users/" + str(self.uid) + "/listings/")
        r.raise_for_status()

        return r.json()

    def get_listing(self, listing_id):
        """ Gets listings for uid on api """
        assert(self._access_token and self.uid)

        r = self._session.get(API_URL + "/v1/listings/" + str(listing_id), params={'_format': 'v1_legacy_for_p3'})
        r.raise_for_status()

        return r.json()

    def get_reservations(self, offset=0):
        """ Gets all user's reservations (max 50) for next 120 days """
        assert(self._access_token and self.uid)

        date = datetime.date.today()
        delta = datetime.timedelta(days=120)

        future_date = date + delta

        r = self._session.get(API_URL + "/v2/reservations/", 
            params={
            '_order': 'start_date',
            '_limit': 50,
            'start_date': date.strftime("%Y-%m-%d"),
            '_offset': offset,
            'host_id': self.uid,
            'end_date': future_date.strftime("%Y-%m-%d"),
            })
        r.raise_for_status()

        return r.json()

    def get_reservation(self, reservation_id):
        """ Takes reservation uid or confirmation code, returns details. """
        assert(self._access_token and self.uid)

        r = self._session.get(API_URL + "/v2/reservations/" + str(reservation_id), 
            params={
            '_format': 'v1_legacy_long',
            'include_shared_itinerary': 'true',
            })
        r.raise_for_status()

        return r.json()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
