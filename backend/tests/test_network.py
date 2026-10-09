import pytest
from app.infrastructure.models.network import DeviceStatus, NetworkDevice
from app.infrastructure.models.network_sensor import NetworkSensor
from app.infrastructure.schemas.network import SensorStatus
import uuid

def test_sensor_registration():
    # Simulate registration without database dependency
    name = "test_sensor"
    key = "secret_key"
    sensor = NetworkSensor(
        id=uuid.uuid4(),
        name=name,
        sensor_key=key,
        status=SensorStatus.PENDING
    )
    assert sensor.name == name
    assert sensor.status == SensorStatus.PENDING

def test_device_creation():
    # Simulate device creation without database dependency
    device = NetworkDevice(
        mac_address="00:11:22:33:44:55",
        ip_address="192.168.1.100",
        status=DeviceStatus.ONLINE
    )
    assert device.mac_address == "00:11:22:33:44:55"
    assert device.ip_address == "192.168.1.100"
    assert device.status == DeviceStatus.ONLINE
