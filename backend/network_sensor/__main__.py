"""Authorized host sensor for bounded Windows/Linux network telemetry."""

import json
import logging
import os
import platform
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .collectors import collect_network_state, discover_neighbors

logger = logging.getLogger("sentinelops.network_sensor")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


class NetworkSensor:
    def __init__(self, api_url: str, sensor_id: str, sensor_key: str, interval: int = 30):
        self.api_url = api_url.rstrip("/")
        self.sensor_id = sensor_id
        self.sensor_key = sensor_key
        self.interval = max(10, interval)

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Sensor-Id": self.sensor_id,
            "X-Sensor-Key": self.sensor_key,
        }

    def submit(self, payload: Dict[str, Any]) -> None:
        request = urllib.request.Request(
            f"{self.api_url}/api/v1/network/sensor/data",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status >= 400:
                    raise RuntimeError(f"sensor API returned HTTP {response.status}")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"sensor API returned HTTP {exc.code}") from exc

    def collect_once(self) -> Dict[str, Any]:
        state = collect_network_state()
        devices = discover_neighbors()
        now = datetime.now(timezone.utc).isoformat()
        return {
            "submitted_at": now,
            "interfaces": state.get("interfaces", []),
            "snapshot": state.get("snapshot"),
            "health": state.get("health", []),
            "devices": devices,
        }

    def run(self) -> None:
        logger.info("network sensor started on %s", platform.system())
        while True:
            try:
                self.submit(self.collect_once())
                logger.info("network telemetry submitted")
            except Exception as exc:
                logger.warning("telemetry cycle failed: %s", exc)
            time.sleep(self.interval)


def main() -> None:
    sensor_id = os.getenv("SENSOR_ID")
    sensor_key = os.getenv("SENSOR_KEY")
    if not sensor_id or not sensor_key:
        raise SystemExit("SENSOR_ID and SENSOR_KEY are required")
    NetworkSensor(
        api_url=os.getenv("SENTINELOPS_API_URL", os.getenv("FASTAPI_URL", "http://localhost:8000")),
        sensor_id=sensor_id,
        sensor_key=sensor_key,
        interval=int(os.getenv("DISCOVERY_INTERVAL_SECONDS", "30")),
    ).run()


if __name__ == "__main__":
    main()
