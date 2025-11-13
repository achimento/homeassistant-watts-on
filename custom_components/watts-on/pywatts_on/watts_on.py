"""API client for Watts On integration."""

from __future__ import annotations
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import os
import re
import requests
import time
import logging
from collections import defaultdict

_LOGGER = logging.getLogger(__name__)

TENANT = "wattsenergyassistant.onmicrosoft.com"
POLICY = "b2c_1a_jitmigraion_signup_signin"
CLIENT_ID = "a19dc71d-697e-451a-86c4-cc112b202c90"
REDIRECT_URI = "msauth.com.seasnve.watts://auth"
SCOPES = (
    "https://wattsenergyassistant.onmicrosoft.com/"
    "a19dc71d-697e-451a-86c4-cc112b202c90/Watts.API openid profile offline_access"
)
BASE_B2C = f"https://wattsenergyassistant.b2clogin.com/{TENANT}/{POLICY}"
TOKEN_URL = f"{BASE_B2C}/oauth2/v2.0/token"
AUTH_URL = f"{BASE_B2C}/oauth2/v2.0/authorize"
SELFASSERTED_URL = f"{BASE_B2C}/SelfAsserted"
CONFIRMED_URL = f"{BASE_B2C}/api/CombinedSigninAndSignup/confirmed"


class WattsOnApi:
    """Watts On API client with token persistence support."""

    def __init__(self, username: str, password: str, tokens: dict | None = None):
        self.username = username
        self.password = password
        self.water_device_id: str | None = None
        self.heating_device_id: str | None = None
        self.tokens: dict | None = tokens
        self.session = requests.Session()

    def _is_token_valid(self) -> bool:
        """Check if access token is still valid."""
        if not self.tokens:
            return False
        expires_on = int(self.tokens.get("expires_on", 0))
        return time.time() < (expires_on - 60)

    def ensure_token(self) -> str:
        """Return a valid access token (refresh or login if needed)."""
        if self._is_token_valid():
            return self.tokens["access_token"]

        if self.tokens and "refresh_token" in self.tokens:
            _LOGGER.debug("Refreshing access token using refresh_token")
            resp = self.session.post(
                TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "client_id": CLIENT_ID,
                    "scope": SCOPES,
                    "refresh_token": self.tokens["refresh_token"],
                    "redirect_uri": REDIRECT_URI,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                self.tokens = resp.json()
                _LOGGER.info("Token refreshed successfully")
                return self.tokens["access_token"]

            _LOGGER.warning(
                "Refresh failed (%s), falling back to full login",
                resp.status_code,
            )

        # If no valid tokens - full login
        self.tokens = self.login()
        return self.tokens["access_token"]
    
    def _pkce_pair(self):
        verifier = base64.urlsafe_b64encode(os.urandom(64)).decode().rstrip("=")
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode()).digest()
        ).decode().rstrip("=")
        return verifier, challenge

    def _first_match(self, pattern, text, group=1):
        m = re.search(pattern, text)
        return m.group(group) if m else None

    def _require(self, value, what):
        if not value:
            raise RuntimeError(f"Could not find {what}; login flow may have changed.")

    def login(self) -> dict:
        """Do the full PKCE login flow and return fresh tokens."""
        code_verifier, code_challenge = self._pkce_pair()

        # Start auth flow
        auth_params = {
            "client_id": CLIENT_ID,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "response_mode": "query",
            "scope": SCOPES,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "prompt": "select_account",
            "client_info": "1",
        }
        r = self.session.get(AUTH_URL, params=auth_params, allow_redirects=True, timeout=30)
        r.raise_for_status()

        # Extract StateProperties
        tx_val = self._first_match(r"StateProperties=([^&\"'<> ]+)", r.url) \
            or self._first_match(r"StateProperties=([^&\"'<> ]+)", r.text)
        self._require(tx_val, "StateProperties")

        csrf_cookie = self.session.cookies.get("x-ms-cpim-csrf")
        self._require(csrf_cookie, "x-ms-cpim-csrf cookie")

        # POST SelfAsserted with credentials
        sa_params = {"tx": f"StateProperties={tx_val}", "p": POLICY}
        sa_headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRF-TOKEN": csrf_cookie,
            "Origin": "https://wattsenergyassistant.b2clogin.com",
            "Referer": r.url.split("#")[0],
        }
        sa_payload = {"request_type": "RESPONSE", "signInName": self.username, "password": self.password}
        sa = self.session.post(SELFASSERTED_URL, params=sa_params, data=sa_payload, headers=sa_headers, timeout=30)
        if sa.status_code not in (200, 204):
            raise RuntimeError(f"Login step failed: {sa.status_code} {sa.text[:200]}")

        # Confirm
        conf_params = {"rememberMe": "false", "csrf_token": csrf_cookie, "tx": f"StateProperties={tx_val}", "p": POLICY}
        conf = self.session.get(CONFIRMED_URL, params=conf_params, allow_redirects=False, timeout=30)
        if conf.status_code not in (302, 303):
            raise RuntimeError(f"Expected redirect, got {conf.status_code}")

        redirect_url = conf.headers.get("Location", "")
        self._require(redirect_url, "redirect URL with code")
        auth_code = self._first_match(r"[?&]code=([^&\s\"'>]+)", redirect_url)
        self._require(auth_code, "authorization code")

        # Exchange code for tokens
        token_data = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "scope": SCOPES,
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier,
        }
        tok = self.session.post(TOKEN_URL, data=token_data, timeout=30)
        if tok.status_code != 200:
            raise RuntimeError(f"Token exchange failed: {tok.status_code} {tok.text[:200]}")

        return tok.json()
    
    def extract_summations(self, data):
        now = datetime.now(timezone.utc)
        day_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        yesterday_start = day_start - timedelta(days=1)
        first_of_this_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        ytd_start = datetime(now.year, 1, 1, tzinfo=timezone.utc)
        week_start = day_start - timedelta(days=now.weekday())

        month_total = 0.0
        yesterday_total = 0.0
        week_total = 0.0
        ytd_total = 0.0

        for d in data:
            try:
                ts = d.get("sd") or d.get("SD")
                val = d.get("vol") or d.get("En")
                if ts is None or val is None:
                    continue

                if isinstance(ts, str):
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                else:
                    dt = datetime.fromtimestamp(ts, tz=timezone.utc)

                if not val < 0:
                    fval = float(val)

                    if yesterday_start <= dt <= day_start:
                        yesterday_total += fval

                    if dt >= week_start:
                        week_total += fval

                    if dt >= first_of_this_month:
                        month_total += fval

                    if dt >= ytd_start:
                        ytd_total += fval
            except Exception:
                continue

        return {
            "statistics_week": week_total,
            "statistics_month": month_total,
            "statistics_year": ytd_total,
            "statistics_yesterday": yesterday_total,
        }
    
    def build_timeseries(self, data, interval: str = "daily"):
        """
        Build time-series statistics.

        Args:
            data: Raw list of readings from API.
            interval: Aggregation period: 'hourly', 'daily', 'weekly', 'monthly', 'raw'.

        Returns:
            A list of dictionaries: [{"datetime": ISO8601, "value": float}, ...]
        """
        # Prepare accumulator
        grouped = defaultdict(float)

        for d in data:
            ts = d.get("sd") or d.get("SD")
            val = d.get("vol") or d.get("En")
            if ts is None or val is None:
                continue

            try:
                if isinstance(ts, str):
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                else:
                    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                fval = float(val)
            except Exception:
                continue

            if interval == "hourly":
                key = dt.replace(minute=0, second=0, microsecond=0)
            elif interval == "daily":
                key = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            elif interval == "weekly":
                key = dt - timedelta(days=dt.weekday())
                key = key.replace(hour=0, minute=0, second=0, microsecond=0)
            elif interval == "monthly":
                key = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                key = dt

            grouped[key] += fval

        stats = [
            {"datetime": k.isoformat(), "value": round(v, 3)}
            for k, v in sorted(grouped.items())
        ]

        return stats

    
    def fetch_devices(self):
        url = "https://p.watts-energy.dk/provisioning/api/v1/locations"
        headers = {"Authorization": f"Bearer {self.tokens['access_token']}"}
        try:
            json_response = requests.get(url, headers=headers, timeout=30).json()
            devices = json_response[0]["devices"]
            heating_devices = [d for d in devices if "heating" in d["utilityType"].lower()]
            if len(heating_devices) > 0:
                self.heating_device_id = heating_devices[0]["deviceId"]
            else:
                self.heating_device_id = ""
            water_devices = [d for d in devices if "water" in d["utilityType"].lower()]
            if len(water_devices) > 0:
                self.water_device_id = water_devices[0]["deviceId"]
            else:
                self.water_device_id = ""
        except Exception as e:
            return

    def fetch_water(self, token: str):
        """Fetch water data from API."""
        return self.session.get(
            f"https://p.watts-energy.dk/water/api/data/{self.water_device_id}",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "startDate": "1900-01-01 00:00:00 +0000",
                "endDate": "2100-01-01 00:00:00 +0000",
            },
            timeout=30,
        ).json()

    def fetch_heating(self, token: str):
        """Fetch heating data from API."""
        return self.session.get(
            f"https://p.watts-energy.dk/heating/api/v1/devices/{self.heating_device_id}/data",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "fromDate": "1900-01-01 00:00:00 +0000",
                "toDate": "2100-01-01 00:00:00 +0000",
            },
            timeout=30,
        ).json()
    
    def fetch_data(self) -> dict:
        """
        Fetch cumulative water and heating statistics.
        """
        token = self.ensure_token()
        raw_heating = self.fetch_heating(token)
        raw_water = self.fetch_water(token)

        heating_data = raw_heating if isinstance(raw_heating, list) else raw_heating.get("data", [])
        water_data = raw_water if isinstance(raw_water, list) else raw_water.get("data", [])

        return {
            "water": {
                **self.extract_summations(water_data),
                "statistics": self.build_timeseries(water_data, "daily"),
            },
            "heating": {
                **self.extract_summations(heating_data),
                "statistics": self.build_timeseries(heating_data, "daily"),
            },
        }
