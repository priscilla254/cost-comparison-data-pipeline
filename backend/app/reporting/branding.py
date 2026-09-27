"""Brand profile for report exports and AI report copy (logo, footer, colours, fonts)."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator

REPO_ROOT = Path(__file__).resolve().parents[3]
BRANDING_YAML = REPO_ROOT / "branding.yaml"
BRANDING_EXAMPLE_YAML = REPO_ROOT / "branding.example.yaml"

# Neutral defaults mirror branding.example.yaml (no client-specific identity).
_DEFAULTS: dict = {
    "company_name": "Your Company Name",
    "registration_number": "CN 00000000",
    "website": "example.com",
    "logo_path": "backend/app/reporting/assets/logos/company_logo.png",
    "font_family": "DM Sans",
    "font_body_file": "DMSans-Regular.ttf",
    "font_body_bold_file": "DMSans-Bold.ttf",
    "heading_font_family": "Fraunces",
    "font_heading_file": "Fraunces-SemiBold.ttf",
    "accent_colour": "#235d45",
    "text_colour": "#1a1814",
    "muted_colour": "#66615b",
    "surface_colour": "#f4f1ea",
}

_COLOUR_FIELDS = ("accent_colour", "text_colour", "muted_colour", "surface_colour")


class BrandProfile(BaseModel):
    company_name: str = Field(default=_DEFAULTS["company_name"])
    registration_number: str = Field(default=_DEFAULTS["registration_number"])
    website: str = Field(default=_DEFAULTS["website"])
    logo_path: str = Field(default=_DEFAULTS["logo_path"])
    font_family: str = Field(default=_DEFAULTS["font_family"])
    font_body_file: str = Field(default=_DEFAULTS["font_body_file"])
    font_body_bold_file: str = Field(default=_DEFAULTS["font_body_bold_file"])
    heading_font_family: str = Field(default=_DEFAULTS["heading_font_family"])
    font_heading_file: str = Field(default=_DEFAULTS["font_heading_file"])
    accent_colour: str = Field(default=_DEFAULTS["accent_colour"])
    text_colour: str = Field(default=_DEFAULTS["text_colour"])
    muted_colour: str = Field(default=_DEFAULTS["muted_colour"])
    surface_colour: str = Field(default=_DEFAULTS["surface_colour"])

    @field_validator(*_COLOUR_FIELDS, mode="before")
    @classmethod
    def _normalize_colour(cls, value, info):
        if value is None or str(value).strip() == "":
            return _DEFAULTS[info.field_name]
        text = str(value).strip()
        if not text.startswith("#"):
            text = f"#{text}"
        return text

    def resolved_logo_path(self) -> Path | None:
        """Return an existing logo Path, or None if missing."""
        raw = (self.logo_path or "").strip()
        if not raw:
            return None
        path = Path(raw)
        if not path.is_absolute():
            path = REPO_ROOT / path
        return path if path.is_file() else None

    def pdf_footer_left_lines(self) -> list[str]:
        """Company name + registration for the PDF footer left column."""
        lines: list[str] = []
        if self.company_name.strip():
            lines.append(self.company_name.strip())
        if self.registration_number.strip():
            lines.append(self.registration_number.strip())
        return lines


def _load_yaml_file(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Branding file must be a mapping: {path}")
    return data


def _coerce_legacy_footer(overrides: dict) -> dict:
    """Map old legal_footer_lines into company_name / registration_number if needed."""
    data = dict(overrides)
    legacy = data.pop("legal_footer_lines", None)
    if legacy is None:
        return data
    if isinstance(legacy, str):
        text = legacy.strip()
        if "|" in text and "\n" not in text:
            lines = [part.strip() for part in text.split("|") if part.strip()]
        else:
            lines = [line.strip() for line in text.splitlines() if line.strip()]
    elif isinstance(legacy, list):
        lines = [str(line).strip() for line in legacy if str(line).strip()]
    else:
        return data
    if lines and not data.get("company_name"):
        data["company_name"] = lines[0]
    if len(lines) > 1 and not data.get("registration_number"):
        data["registration_number"] = lines[1]
    return data


def _from_env() -> dict:
    """Build partial profile dict from BRAND_* environment variables."""
    data: dict = {}
    company = os.getenv("BRAND_COMPANY_NAME", "").strip()
    if company:
        data["company_name"] = company

    reg = os.getenv("BRAND_REGISTRATION_NUMBER", "").strip()
    if reg:
        data["registration_number"] = reg

    footer = os.getenv("BRAND_LEGAL_FOOTER_LINES", "").strip()
    if footer:
        data["legal_footer_lines"] = footer

    website = os.getenv("BRAND_WEBSITE", "").strip()
    if website:
        data["website"] = website

    logo = os.getenv("BRAND_LOGO_PATH", "").strip()
    if logo:
        data["logo_path"] = logo

    font = os.getenv("BRAND_FONT_FAMILY", "").strip()
    if font:
        data["font_family"] = font

    body = os.getenv("BRAND_FONT_BODY_FILE", "").strip()
    if body:
        data["font_body_file"] = body

    body_bold = os.getenv("BRAND_FONT_BODY_BOLD_FILE", "").strip()
    if body_bold:
        data["font_body_bold_file"] = body_bold

    heading_family = os.getenv("BRAND_HEADING_FONT_FAMILY", "").strip()
    if heading_family:
        data["heading_font_family"] = heading_family

    heading = os.getenv("BRAND_FONT_HEADING_FILE", "").strip()
    if heading:
        data["font_heading_file"] = heading

    for field in _COLOUR_FIELDS:
        env_base = f"BRAND_{field.upper()}"
        value = (
            os.getenv(env_base, "").strip()
            or os.getenv(env_base.replace("COLOUR", "COLOR"), "").strip()
        )
        if value:
            data[field] = value

    return _coerce_legacy_footer(data)


def _merged_defaults(overrides: dict) -> dict:
    cleaned = _coerce_legacy_footer(overrides)
    merged = dict(_DEFAULTS)
    for key, value in cleaned.items():
        if key not in merged:
            continue
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        merged[key] = value
    return merged


@lru_cache
def get_brand_profile() -> BrandProfile:
    """
    Load brand settings: branding.yaml if present, else BRAND_* env,
    with gaps filled from neutral defaults (same as branding.example.yaml).
    """
    if BRANDING_YAML.is_file():
        overrides = _load_yaml_file(BRANDING_YAML)
    else:
        overrides = _from_env()
    return BrandProfile(**_merged_defaults(overrides))


def clear_brand_profile_cache() -> None:
    get_brand_profile.cache_clear()
