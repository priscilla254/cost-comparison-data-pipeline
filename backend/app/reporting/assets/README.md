## Reporting Brand Assets

Brand identity for PDF/DOCX exports and AI report prompts is driven by
**`BrandProfile`** ([`../branding.py`](../branding.py)):

1. Copy [`branding.example.yaml`](../../../../branding.example.yaml) to repo-root
   `branding.yaml` (gitignored) and customise, **or**
2. Set `BRAND_*` environment variables (`BRAND_COMPANY_NAME`,
   `BRAND_REGISTRATION_NUMBER`, `BRAND_WEBSITE`, `BRAND_LOGO_PATH`,
   `BRAND_FONT_FAMILY`, `BRAND_FONT_BODY_FILE`, `BRAND_FONT_BODY_BOLD_FILE`,
   `BRAND_HEADING_FONT_FAMILY`, `BRAND_FONT_HEADING_FILE`, `BRAND_ACCENT_COLOUR`,
   `BRAND_TEXT_COLOUR`, `BRAND_MUTED_COLOUR`, `BRAND_SURFACE_COLOUR`).

### Asset layout

Put logo and font files under:

- `assets/logos/` — referenced by `logo_path` in branding config
- `assets/fonts/` — TTF files named by `font_body_file` / `font_heading_file`

Example:

```yaml
company_name: "Your Company Name"
registration_number: "CN 00000000"
website: "example.com"
logo_path: "backend/app/reporting/assets/logos/company_logo.png"
font_family: "DM Sans"
font_body_file: "DMSans-Regular.ttf"
font_body_bold_file: "DMSans-Bold.ttf"
heading_font_family: "Fraunces"
font_heading_file: "Fraunces-SemiBold.ttf"
accent_colour: "#235d45"
text_colour: "#1a1814"
muted_colour: "#66615b"
surface_colour: "#f4f1ea"
```

The bundled DM Sans and Fraunces fonts are licensed under the SIL Open Font
License 1.1 (Google Fonts).

### Notes

- Missing logo files are skipped (reports export without a header logo).
- Relative asset paths for WeasyPrint are resolved using `base_url` set to the
  `reporting` directory when the logo lives under this tree.
- Logo files under `assets/logos/` remain gitignored; keep a local copy or
  point `logo_path` at your private brand asset.
