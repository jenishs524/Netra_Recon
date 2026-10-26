from __future__ import annotations

import socket
from unittest.mock import patch

from netra_recon.modules import ipv6_reachability_test


def _addrinfo(address: str) -> tuple:
    return (
        socket.AF_INET6,
        socket.SOCK_STREAM,
        socket.IPPROTO_TCP,
        "",
        (address, 443, 0, 0),
    )


def test_resolve_ipv6_addresses_resolves_domain_aaaa_records() -> None:
    records = [_addrinfo("2001:db8::1"), _addrinfo("2001:db8::1"), _addrinfo("2001:db8::2")]
    with patch.object(socket, "getaddrinfo", return_value=records) as getaddrinfo:
        addresses = ipv6_reachability_test.resolve_ipv6_addresses("example.com", 1)

    assert addresses == ["2001:db8::1"]
    getaddrinfo.assert_called_once_with(
        "example.com", None, family=socket.AF_INET6, type=socket.SOCK_STREAM
    )


def test_resolve_ipv6_addresses_accepts_literal_and_bounds_cidr() -> None:
    assert ipv6_reachability_test.resolve_ipv6_addresses("2001:db8::1", 4) == [
        "2001:db8::1"
    ]
    assert ipv6_reachability_test.resolve_ipv6_addresses("2001:db8::/120", 2) == [
        "2001:db8::1",
        "2001:db8::2",
    ]


def test_run_probes_resolved_domain_ipv6_addresses() -> None:
    with (
        patch(
            "sys.argv",
            [
                "ipv6_reachability_test.py",
                "example.com",
                "1",
                '{"timeout": 1, "max_hosts": 1}',
            ],
        ),
        patch.object(
            ipv6_reachability_test,
            "resolve_ipv6_addresses",
            return_value=["2001:db8::1"],
        ) as resolve,
        patch.object(ipv6_reachability_test, "ping6", return_value=True) as ping,
        patch.object(socket, "gethostbyaddr", return_value=("host.example.com", [], [])),
        patch.object(ipv6_reachability_test, "EXPORT_SETTINGS", {"enable_txt_export": False}),
    ):
        ipv6_reachability_test.main()

    resolve.assert_called_once_with("example.com", 1)
    ping.assert_called_once_with("2001:db8::1", 1.0)
