"""
World Bank REST API Client.
Fetches real-time macroeconomic indicators directly from World Bank Open Data endpoints.
"""

from typing import Optional, Dict, Any, List
import json
import urllib.request
import urllib.error
import pandas as pd


class WorldBankClient:
    """Production-grade client for querying World Bank Economic Data."""

    BASE_URL = "https://api.worldbank.org/v2"
    INDICATOR_GDP = "NY.GDP.MKTP.CD"  # GDP in current US$

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {"User-Agent": "MacroPulse-Engine/1.0"}

    def fetch_indicator(
        self,
        country_code: str,
        indicator: str = INDICATOR_GDP,
        start_year: int = 1960,
        end_year: int = 2024,
    ) -> pd.DataFrame:
        """
        Fetches time-series records for a country and indicator via World Bank REST API.
        
        Args:
            country_code: ISO-2 or ISO-3 country code (e.g., 'USA', 'EGY', 'WLD').
            indicator: World Bank indicator identifier.
            start_year: Beginning of time-series window.
            end_year: End of time-series window.
            
        Returns:
            Normalized pandas DataFrame with ['Year', 'GDP', 'Country Code', 'Country Name'].
        """
        endpoint = (
            f"{self.BASE_URL}/country/{country_code}/indicator/{indicator}"
            f"?date={start_year}:{end_year}&format=json&per_page=100"
        )

        req = urllib.request.Request(endpoint, headers=self.headers)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))

            # World Bank API returns [metadata, records] on success
            if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
                return pd.DataFrame(columns=["Year", "GDP", "Country Code", "Country Name"])

            records: List[Dict[str, Any]] = payload[1]
            rows = []
            for item in records:
                value = item.get("value")
                year_str = item.get("date")
                
                if year_str and year_str.isdigit():
                    rows.append({
                        "Year": int(year_str),
                        "GDP": float(value) if value is not None else None,
                        "Country Code": item.get("countryiso3code") or country_code.upper(),
                        "Country Name": item.get("country", {}).get("value", country_code.upper()),
                    })

            df = pd.DataFrame(rows)
            if not df.empty:
                df = df.sort_values("Year", ascending=True).reset_index(drop=True)
            return df

        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
            # Graceful fallback: return empty typed dataframe instead of breaking runtime
            return pd.DataFrame(columns=["Year", "GDP", "Country Code", "Country Name"])
