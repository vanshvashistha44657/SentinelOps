from network_sensor import collectors


def test_windows_unreachable_reply_is_not_a_successful_ping(monkeypatch):
    monkeypatch.setattr(collectors.platform, "system", lambda: "Windows")
    monkeypatch.setattr(collectors, "_run", lambda *args, **kwargs: "Reply from 192.168.1.10: Destination host unreachable.")
    assert collectors._reachability_check("192.168.1.1", "GATEWAY")["status"] == "FAIL"
    monkeypatch.setattr(collectors, "_run", lambda *args, **kwargs: "Reply from 192.168.1.1: bytes=32 time<1ms TTL=64")
    assert collectors._reachability_check("192.168.1.1", "GATEWAY")["status"] == "PASS"


def test_neighbor_discovery_excludes_broadcast_entries(monkeypatch):
    monkeypatch.setattr(collectors.platform, "system", lambda: "Windows")
    monkeypatch.setattr(collectors, "_run", lambda *args, **kwargs: "192.168.1.255 ff-ff-ff-ff-ff-ff static\n192.168.1.1 aa-bb-cc-dd-ee-ff dynamic")
    assert [item["ip_address"] for item in collectors.discover_neighbors()] == ["192.168.1.1"]


def test_dns_resolution_has_a_bounded_deadline(monkeypatch):
    calls = []
    def run(command, timeout):
        calls.append((command, timeout))
        return ""
    monkeypatch.setattr(collectors, "_run", run)
    assert collectors._dns_check("192.168.1.1")["status"] == "FAIL"
    assert calls[0][1] == 3
