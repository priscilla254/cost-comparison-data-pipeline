"""Unit tests for money formatting in report exports."""

from __future__ import annotations

from decimal import Decimal

from backend.app.services.report_export_service import _format_money, _prepare_docx_context


def test_format_money():
    assert _format_money(3257750) == "£3,257,750"
    assert _format_money(Decimal("1250.5")) == "£1,250.50"
    assert _format_money(-86250) == "-£86,250"
    assert _format_money(0) == "£0"
    assert _format_money(None) == ""
    assert _format_money("TBC") == "TBC"


def test_prepare_context_formats_tender_rows():
    payload = {
        "report_context": {
            "commercial": {
                "construction_budget": 3171500,
                "tender_comparison": [
                    {
                        "contractor": "Apex Build Ltd",
                        "final_adjusted_tender_sum": 3257750,
                        "variance_to_construction_budget": 86250,
                    }
                ],
            }
        }
    }
    context = _prepare_docx_context(payload)
    row = context["tender_rows"][0]
    assert row["contractor"] == "Apex Build Ltd"
    assert row["final_adjusted_tender_sum"] == "£3,257,750"
    assert row["variance_to_construction_budget"] == "£86,250"
    assert context["construction_budget"] == "£3,171,500"
    assert context["tender_review_rows"][1]["values"] == ["£3,171,500"]
