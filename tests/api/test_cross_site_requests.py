from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

WRITE = "/api/plugins/rescan"


@pytest.mark.parametrize(
    "headers",
    [
        {"Sec-Fetch-Site": "cross-site", "Origin": "https://evil.example"},
        {"Sec-Fetch-Site": "same-site", "Origin": "http://localhost:3000"},
        {"Origin": "https://evil.example"},
        {"Origin": "null"},
    ],
)
def test_cross_site_writes_are_rejected(client: TestClient, headers: dict[str, str]) -> None:
    response = client.post(WRITE, headers=headers)

    assert response.status_code == 403
    assert response.json() == {"detail": "Cross-site requests to Meet2Notes are not allowed"}


@pytest.mark.parametrize(
    "headers",
    [
        {"Sec-Fetch-Site": "same-origin", "Origin": "http://testserver"},
        {"Origin": "http://testserver"},
        {},
    ],
)
def test_same_origin_and_non_browser_writes_are_allowed(
    client: TestClient, headers: dict[str, str]
) -> None:
    assert client.post(WRITE, headers=headers).status_code == 200


def test_cross_site_reads_are_not_blocked(client: TestClient) -> None:
    response = client.get(
        "/api/health", headers={"Sec-Fetch-Site": "cross-site", "Origin": "https://evil.example"}
    )

    # The browser withholds the response without CORS headers; the server need not refuse it.
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
