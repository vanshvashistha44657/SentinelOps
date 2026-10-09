from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import RBAC
from app.application.services.audit import AuditService
from app.application.services.network import NetworkService
from app.infrastructure.models.network import NetworkDevice, NetworkHealthMeasurement, NetworkInterface, NetworkSnapshot
from app.infrastructure.models.network_sensor import NetworkSensor
from app.infrastructure.repositories.audit import SQLAlchemyAuditRepository
from app.infrastructure.schemas.network import (
    NetworkDeviceResponse,
    NetworkHealthResponse,
    NetworkInterfaceResponse,
    NetworkSnapshotResponse,
    SensorDataSubmission,
    SensorEnrollmentResponse,
    SensorRegistration,
    SensorResponse,
)

router = APIRouter(prefix="/network", tags=["Network Intelligence"])


def get_network_service(db: Session = Depends(get_db)) -> NetworkService:
    return NetworkService(db)


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    return AuditService(SQLAlchemyAuditRepository(db))


def get_sensor_from_headers(
    sensor_id: str = Header(..., alias="X-Sensor-Id"),
    sensor_key: str = Header(..., alias="X-Sensor-Key"),
    service: NetworkService = Depends(get_network_service),
) -> NetworkSensor:
    sensor = service.authenticate_sensor(sensor_id, sensor_key)
    if not sensor:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive sensor credentials")
    return sensor


@router.post("/sensor/register", response_model=SensorEnrollmentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RBAC("admin:write"))])
def register_sensor(
    registration: SensorRegistration,
    request: Request,
    current_user=Depends(get_current_user),
    service: NetworkService = Depends(get_network_service),
    audit: AuditService = Depends(get_audit_service),
):
    sensor, key = service.enroll_sensor(registration.name, registration.platform, registration.version, registration.capabilities, current_user.id)
    audit.log_action(current_user.id, request.client.host, "network_sensors", "SENSOR_REGISTER", None, {"sensor_id": str(sensor.id), "name": sensor.name})
    return {"sensor": sensor, "sensor_key": key}


@router.get("/sensors", response_model=List[SensorResponse], dependencies=[Depends(RBAC("network:view"))])
def list_sensors(db: Session = Depends(get_db)):
    return db.query(NetworkSensor).order_by(NetworkSensor.created_at.desc()).all()


@router.post("/admin/sensor/activate/{sensor_id}", response_model=SensorResponse, dependencies=[Depends(RBAC("admin:write"))])
def activate_sensor(
    sensor_id: UUID,
    request: Request,
    current_user=Depends(get_current_user),
    service: NetworkService = Depends(get_network_service),
    audit: AuditService = Depends(get_audit_service),
):
    sensor = service.activate_sensor(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    audit.log_action(current_user.id, request.client.host, "network_sensors", "SENSOR_ACTIVATE", None, {"sensor_id": str(sensor_id)})
    return sensor


@router.post("/admin/sensor/revoke/{sensor_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RBAC("admin:write"))])
def revoke_sensor(
    sensor_id: UUID,
    request: Request,
    current_user=Depends(get_current_user),
    service: NetworkService = Depends(get_network_service),
    audit: AuditService = Depends(get_audit_service),
):
    if not service.revoke_sensor(sensor_id):
        raise HTTPException(status_code=404, detail="Sensor not found")
    audit.log_action(current_user.id, request.client.host, "network_sensors", "SENSOR_REVOKE", None, {"sensor_id": str(sensor_id)})


@router.post("/sensor/data")
def submit_sensor_data(
    submission: SensorDataSubmission,
    sensor: NetworkSensor = Depends(get_sensor_from_headers),
    service: NetworkService = Depends(get_network_service),
):
    return service.process_submission(sensor, submission)


@router.get("/devices", response_model=List[NetworkDeviceResponse], dependencies=[Depends(RBAC("network:view"))])
def get_devices(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    query = db.query(NetworkDevice)
    if status_filter:
        query = query.filter(NetworkDevice.status == status_filter)
    return query.order_by(NetworkDevice.last_seen.desc()).offset((page - 1) * size).limit(size).all()


@router.get("/interfaces", response_model=List[NetworkInterfaceResponse], dependencies=[Depends(RBAC("network:view"))])
def get_interfaces(db: Session = Depends(get_db), sensor_id: Optional[UUID] = None):
    query = db.query(NetworkInterface)
    if sensor_id:
        query = query.filter(NetworkInterface.sensor_id == sensor_id)
    return query.order_by(NetworkInterface.observed_at.desc()).all()


@router.get("/overview", dependencies=[Depends(RBAC("network:view"))])
def get_overview(db: Session = Depends(get_db)):
    sensor = db.query(NetworkSensor).order_by(NetworkSensor.last_telemetry_at.desc().nullslast()).first()
    snapshot = db.query(NetworkSnapshot).order_by(NetworkSnapshot.captured_at.desc()).first()
    return {
        "sensor": SensorResponse.model_validate(sensor).model_dump(mode="json") if sensor else None,
        "snapshot": NetworkSnapshotResponse.model_validate(snapshot).model_dump(mode="json") if snapshot else None,
        "device_count": db.query(NetworkDevice).count(),
        "online_device_count": db.query(NetworkDevice).filter(NetworkDevice.status == "ONLINE").count(),
        "limitations": [
            "ARP and neighbor tables provide limited local visibility, not a complete inventory.",
            "VLANs, client isolation, sleeping devices, firewalls, and OS permissions can hide devices.",
        ],
    }


@router.get("/health", response_model=List[NetworkHealthResponse], dependencies=[Depends(RBAC("network:view"))])
def get_health(db: Session = Depends(get_db), sensor_id: Optional[UUID] = None, limit: int = Query(100, ge=1, le=500)):
    query = db.query(NetworkHealthMeasurement)
    if sensor_id:
        query = query.filter(NetworkHealthMeasurement.sensor_id == sensor_id)
    return query.order_by(NetworkHealthMeasurement.measured_at.desc()).limit(limit).all()


@router.get("/history", dependencies=[Depends(RBAC("network:view"))])
def get_history(
    db: Session = Depends(get_db),
    sensor_id: Optional[UUID] = None,
    since: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=500),
):
    query = db.query(NetworkSnapshot)
    if sensor_id:
        query = query.filter(NetworkSnapshot.sensor_id == sensor_id)
    if since:
        query = query.filter(NetworkSnapshot.captured_at >= since)
    return query.order_by(NetworkSnapshot.captured_at.desc()).limit(limit).all()
