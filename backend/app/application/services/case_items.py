from typing import Optional, List
from uuid import UUID, uuid4
import shutil
import os
from fastapi import UploadFile
from app.infrastructure.repositories.cases import SQLAlchemyCaseRepository
from app.infrastructure.models.incidents import AnalystNote, Evidence, Attachment, Case, Alert, Incident
from app.infrastructure.schemas.case_items import NoteCreate, NoteResponse, EvidenceCreate, EvidenceResponse
from sqlalchemy.orm import Session

# Configuration for file storage
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class CaseItemService:
    def __init__(self, db: Session):
        self.db = db

    # Notes
    def add_note(self, case_id: UUID, note_in: NoteCreate, author_id: UUID) -> NoteResponse:
        note = AnalystNote(case_id=case_id, content=note_in.content, author_id=author_id)
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return NoteResponse.model_validate(note)

    def get_notes(self, case_id: UUID) -> List[NoteResponse]:
        notes = self.db.query(AnalystNote).filter(AnalystNote.case_id == case_id).all()
        return [NoteResponse.model_validate(n) for n in notes]

    # Evidence
    def add_evidence(self, case_id: UUID, evidence_in: EvidenceCreate, user_id: UUID) -> EvidenceResponse:
        evidence = Evidence(case_id=case_id, **evidence_in.model_dump(), added_by_id=user_id)
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return EvidenceResponse.model_validate(evidence)

    def get_evidence(self, case_id: UUID) -> List[EvidenceResponse]:
        evidence = self.db.query(Evidence).filter(Evidence.case_id == case_id).all()
        return [EvidenceResponse.model_validate(e) for e in evidence]

    # Attachments
    def upload_attachment(self, case_id: UUID, file: UploadFile, user_id: UUID) -> Attachment:
        file_path = os.path.join(UPLOAD_DIR, f"{uuid4()}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        attachment = Attachment(
            case_id=case_id,
            file_name=file.filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            mime_type=file.content_type,
            uploaded_by_id=user_id
        )
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment

    # Linking
    def link_alert(self, case_id: UUID, alert_id: UUID):
        case = self.db.query(Case).filter(Case.id == case_id).first()
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if case and alert:
            case.linked_alerts.append(alert)
            self.db.commit()

    def link_incident(self, case_id: UUID, incident_id: UUID):
        case = self.db.query(Case).filter(Case.id == case_id).first()
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if case and incident:
            case.linked_incidents.append(incident)
            self.db.commit()
