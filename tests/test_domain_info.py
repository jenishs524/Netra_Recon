from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import dns.resolver
import pytest

from netra_recon.config import settings
from netra_recon.modules import domain_info


def test_normalize_domain_accepts_url_and_idna_hostname() -> None:
    assert domain_info.normalize_domain("https://www.example.com/path") == "example.com"
    assert domain_info.normalize_domain("bücher.de") == "xn--bcher-kva.de"


@pytest.mark.parametrize(
    "target",
    [
        "",
        "ftp://example.com",
        "https://user:password@example.com",
        "not a domain",
        "example..com",
        "192.0.2.10",
    ],
)
def test_normalize_domain_rejects_invalid_targets(target: str) -> None:
    with pytest.raises(ValueError):
        domain_info.normalize_domain(target)


def test_fetch_dns_records_distinguishes_missing_record_from_lookup_error() -> None:
    class FakeResolver:
        def resolve(self, _domain: str, record_type: str, lifetime: int) -> list[str]:
            assert lifetime == 5
            if record_type == "A":
                return ["192.0.2.1"]
            raise dns.resolver.NoAnswer()

    with patch.object(domain_info.dns.resolver, "Resolver", return_value=FakeResolver()):
        records, errors = domain_info.fetch_dns_records("example.com", 5)

    assert records["A"] == ["192.0.2.1"]
    assert all(records[record_type] == [] for record_type in domain_info.DNS_RECORD_TYPES[1:])
    assert errors == {}


def test_fetch_dns_records_reports_timeouts() -> None:
    class FakeResolver:
        def resolve(self, _domain: str, _record_type: str, lifetime: int) -> list[str]:
            raise dns.resolver.LifetimeTimeout(timeout=lifetime, errors=[])

    with patch.object(domain_info.dns.resolver, "Resolver", return_value=FakeResolver()):
        records, errors = domain_info.fetch_dns_records("example.com", 3)

    assert all(not values for values in records.values())
    assert errors["A"] == "DNS lookup timed out after 3 seconds."


def test_parse_rdap_domain_and_contacts_handles_domain_response_shape() -> None:
    rdap = {
        "ldhName": "EXAMPLE.COM",
        "handle": "12345",
        "status": ["active"],
        "secureDNS": {"delegationSigned": True},
        "nameservers": [{"ldhName": "ns1.example.com"}],
        "entities": [
            {
                "roles": ["registrar"],
                "vcardArray": [
                    "vcard",
                    [["fn", {}, "text", "Example Registrar"], ["email", {}, "text", "r@example.com"]],
                ],
            }
        ],
        "events": [{"eventAction": "registration", "eventDate": "2025-01-01"}],
    }

    fields = dict(domain_info.parse_rdap_domain(rdap))
    assert fields["Registrar"] == "Example Registrar"
    assert fields["Nameservers"] == "ns1.example.com"
    assert fields["DNSSEC"] == "Signed"
    assert domain_info.parse_rdap_entities(rdap) == [
        ("registrar", "Example Registrar", "r@example.com")
    ]
    assert domain_info.parse_rdap_events(rdap) == [("registration", "2025-01-01")]


def test_fetch_rdap_surfaces_http_errors() -> None:
    response = Mock()
    response.raise_for_status.side_effect = domain_info.requests.HTTPError("404 Not Found")
    with patch.object(domain_info.requests, "get", return_value=response):
        data, error = domain_info.fetch_rdap("example.com", 5)

    assert data is None
    assert error is not None and "404 Not Found" in error


def test_run_returns_structured_data_and_writes_json(tmp_path: Path) -> None:
    rdap = {
        "ldhName": "EXAMPLE.COM",
        "handle": "12345",
        "status": ["active"],
        "entities": [],
        "events": [],
    }
    with (
        patch.object(
            domain_info,
            "fetch_dns_records",
            return_value=(
                {record_type: [] for record_type in domain_info.DNS_RECORD_TYPES},
                {},
            ),
        ),
        patch.object(domain_info, "fetch_rdap", return_value=(rdap, None)),
        patch.object(domain_info, "RESULTS_DIR", str(tmp_path)),
        patch.dict(
            settings.EXPORT_SETTINGS,
            {"enable_txt_export": False, "enable_json_export": True},
        ),
    ):
        report = domain_info.run("https://www.example.com/path", opts={"timeout": 5})

    output = tmp_path / "example.com" / "domain_info.json"
    assert report["target"] == "example.com"
    assert report["rdap"]["domain"]["Domain"] == "EXAMPLE.COM"
    assert output.is_file()
    assert json.loads(output.read_text(encoding="utf-8")) == report


@pytest.mark.parametrize(
    ("target", "threads", "options"),
    [
        ("example.com", 0, {}),
        ("example.com", 1, {"timeout": 0}),
        ("example.com", 1, {"timeout": "invalid"}),
        ("example.com", 1, []),
    ],
)
def test_run_rejects_invalid_options(target: str, threads: int, options: object) -> None:
    with pytest.raises(ValueError):
        domain_info.run(target, threads, options)  # type: ignore[arg-type]
