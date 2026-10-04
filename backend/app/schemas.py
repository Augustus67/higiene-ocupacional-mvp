from datetime import datetime

from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    name: str
    cnpj: str | None = None
    description: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyRead(CompanyBase):
    id: int
    created_at: datetime


class SectorBase(BaseModel):
    name: str
    description: str | None = None
    company_id: int


class SectorCreate(SectorBase):
    pass


class SectorRead(SectorBase):
    id: int
    created_at: datetime


class WorkplaceBase(BaseModel):
    name: str
    description: str | None = None
    company_id: int
    sector_id: int | None = None


class WorkplaceCreate(WorkplaceBase):
    pass


class WorkplaceRead(WorkplaceBase):
    id: int
    created_at: datetime


class WorkerBase(BaseModel):
    name: str
    role: str | None = None
    workplace_id: int


class WorkerCreate(WorkerBase):
    pass


class WorkerRead(WorkerBase):
    id: int
    created_at: datetime


class StandardBase(BaseModel):
    name: str
    description: str | None = None
    is_active: bool = True


class StandardCreate(StandardBase):
    pass


class StandardRead(StandardBase):
    id: int


class ChemicalBase(BaseModel):
    name: str
    cas_number: str | None = None
    description: str | None = None


class ChemicalCreate(ChemicalBase):
    pass


class ChemicalRead(ChemicalBase):
    id: int
    created_at: datetime


class ExposureLimitBase(BaseModel):
    chemical_id: int
    standard_id: int
    limit_value: float
    limit_type: str = "TWA"
    unit: str = "ppm"
    description: str | None = None


class ExposureLimitCreate(ExposureLimitBase):
    pass


class ExposureLimitRead(ExposureLimitBase):
    id: int


class AssessmentBase(BaseModel):
    title: str
    notes: str | None = None
    standard_id: int
    company_id: int
    workplace_id: int | None = None


class AssessmentCreate(AssessmentBase):
    pass


class AssessmentRead(AssessmentBase):
    id: int
    created_at: datetime
