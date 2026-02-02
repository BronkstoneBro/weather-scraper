import json
import re
from typing import Optional
from bs4 import BeautifulSoup

from src.models.weather import WeatherData, BBCWeatherResponse
from src.models.exceptions import (
    DataExtractionException,
    ParserException,
    ValidationException,
)
from .base import BaseParser


class BBCWeatherParser(BaseParser):

    def parse_html(
        self, html_content: str, location_name: Optional[str] = None
    ) -> WeatherData:
        try:
            bbc_response = self.extract_json(html_content)

            if not self.validate_response(bbc_response):
                raise ValidationException(
                    "BBC Weather response validation failed: no forecast data"
                )

            weather_data = WeatherData.from_bbc_response(bbc_response, location_name)

            return weather_data

        except (DataExtractionException, ValidationException) as e:
            raise
        except Exception as e:
            raise ParserException(f"Failed to parse BBC Weather HTML: {str(e)}") from e

    def extract_json(self, html_content: str) -> BBCWeatherResponse:
        try:
            soup = BeautifulSoup(html_content, "html5lib")
            all_scripts = soup.find_all("script")

            weather_json = None

            for script in all_scripts:
                if not script.string:
                    continue

                script_content = script.string.strip()

                if (
                    '"forecasts"' in script_content
                    and '"location_id"' in script_content
                ):
                    json_str = self._extract_json_from_script(script_content)

                    if json_str:
                        try:
                            data = json.loads(json_str)
                            if "data" in data and "forecasts" in data["data"]:
                                weather_json = data
                                break
                        except json.JSONDecodeError:
                            continue

            if not weather_json:
                raise DataExtractionException(
                    "Could not find weather JSON data in HTML"
                )

            bbc_response = BBCWeatherResponse(**weather_json)
            return bbc_response

        except json.JSONDecodeError as e:
            raise DataExtractionException(f"Invalid JSON structure: {str(e)}") from e
        except Exception as e:
            raise DataExtractionException(
                f"Failed to extract JSON from HTML: {str(e)}"
            ) from e

    def _extract_json_from_script(self, script_content: str) -> Optional[str]:
        start_patterns = ['{"options":', '{"data":']
        start_idx = -1

        for pattern in start_patterns:
            idx = script_content.find(pattern)
            if idx >= 0:
                start_idx = idx
                break

        if start_idx < 0:
            return None

        brace_count = 0
        in_string = False
        escape = False
        end_idx = start_idx

        for i in range(start_idx, len(script_content)):
            char = script_content[i]

            if escape:
                escape = False
                continue

            if char == "\\":
                escape = True
                continue

            if char == '"':
                in_string = not in_string
                continue

            if not in_string:
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break

        if end_idx > start_idx and brace_count == 0:
            return script_content[start_idx:end_idx]

        return None

    def extract_location_name(self, html_content: str) -> Optional[str]:
        try:
            soup = BeautifulSoup(html_content, "html5lib")

            title = soup.find("title")
            if title and title.string:
                match = re.match(r"^(.+?)\s*-\s*BBC Weather", title.string)
                if match:
                    return match.group(1).strip()

            meta_title = soup.find("meta", {"property": "og:title"})
            if meta_title and meta_title.get("content"):
                match = re.match(r"^(.+?)\s*-\s*BBC Weather", meta_title["content"])
                if match:
                    return match.group(1).strip()

            location_elem = soup.find(attrs={"data-location-name": True})
            if location_elem:
                return location_elem["data-location-name"]

            return None

        except Exception:
            return None
