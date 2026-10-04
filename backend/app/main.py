from __future__ import annotations

import math
from typing import List, Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Assessment, Chemical, Company, ExposureLimit, Sector, Standard, Worker, Workplace
from app.norms import STANDARDS, SUPPORTED_STANDARDS
from app.schemas import (
    AssessmentCreate,
    AssessmentRead,
    ChemicalCreate,
    ChemicalRead,
    CompanyCreate,
    CompanyRead,
    ExposureLimitCreate,
    ExposureLimitRead,
    SectorCreate,
    SectorRead,
    StandardCreate,
    StandardRead,
    WorkerCreate,
    WorkerRead,
    WorkplaceCreate,
    WorkplaceRead,
)

Base.metadata.create_all(bind=engine)


def seed_default_standards() -> None:
    from app.database import SessionLocal

    with SessionLocal() as db:
        for name in SUPPORTED_STANDARDS:
            existing = db.query(Standard).filter(Standard.name == name).first()
            if not existing:
                db.add(Standard(name=name, description=f"Norma de referência {name}", is_active=True))
        db.commit()


seed_default_standards()

app = FastAPI(
    title="Higiene Ocupacional MVP",
    version="0.1.0",
    description="API para cálculos de ruído, vibração, calor e substâncias químicas."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class NoiseRequest(BaseModel):
    levels: List[float] = Field(..., min_length=1)
    exposure_hours: float = 8.0
    standard: Literal["ACGIH", "NR15", "LINARCH"] = "ACGIH"


class ChemicalItem(BaseModel):
    substance: str
    concentration: float
    limit_value: float
    limit_type: Literal["TWA", "STEL", "CEILING"] = "TWA"


class ChemicalRequest(BaseModel):
    items: List[ChemicalItem] = Field(..., min_length=1)
    standard: Literal["ACGIH", "NR15", "LINARCH"] = "ACGIH"


class VibrationRequest(BaseModel):
    acceleration: float
    exposure_hours: float = 8.0
    vibration_type: Literal["HAND_ARM", "WHOLE_BODY"] = "HAND_ARM"
    standard: Literal["ACGIH", "NR15", "LINARCH"] = "ACGIH"


class HeatRequest(BaseModel):
    wbgt: float
    workload: Literal["LIGHT", "MODERATE", "HEAVY", "VERY_HEAVY"] = "MODERATE"
    standard: Literal["ACGIH", "NR15", "LINARCH"] = "ACGIH"


class NoiseResponse(BaseModel):
    standard: str
    leq: float
    dose_percent: float
    limit_db: float
    exceeds_limit: bool
    interpretation: str


class ChemicalResponse(BaseModel):
    standard: str
    sum_ratio: float
    max_ratio: float
    exceeds_limit: bool
    details: list[dict]


class VibrationResponse(BaseModel):
    standard: str
    a8: float
    limit_value: float
    exceeds_limit: bool
    interpretation: str


class HeatResponse(BaseModel):
    standard: str
    wbgt: float
    allowable_limit: float
    exceeds_limit: bool
    interpretation: str


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "higiene-ocupacional-mvp"}


@app.get("/api/norms")
def list_supported_norms() -> dict:
    return {
        "standards": SUPPORTED_STANDARDS,
        "notes": "Base de referência inicial para apoio ao cálculo e avaliação. A interpretação final deve ser revisada por profissional habilitado.",
    }


@app.get("/api/companies", response_model=list[CompanyRead])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).order_by(Company.id.asc()).all()


@app.post("/api/companies", response_model=CompanyRead)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.name == payload.name).first()
    if company:
        raise HTTPException(status_code=400, detail="Empresa já cadastrada.")

    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@app.get("/api/sectors", response_model=list[SectorRead])
def list_sectors(db: Session = Depends(get_db)):
    return db.query(Sector).order_by(Sector.id.asc()).all()


@app.post("/api/sectors", response_model=SectorRead)
def create_sector(payload: SectorCreate, db: Session = Depends(get_db)):
    if not db.query(Company.id).filter(Company.id == payload.company_id).first():
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")

    sector = Sector(**payload.model_dump())
    db.add(sector)
    db.commit()
    db.refresh(sector)
    return sector


@app.get("/api/workplaces", response_model=list[WorkplaceRead])
def list_workplaces(db: Session = Depends(get_db)):
    return db.query(Workplace).order_by(Workplace.id.asc()).all()


@app.post("/api/workplaces", response_model=WorkplaceRead)
def create_workplace(payload: WorkplaceCreate, db: Session = Depends(get_db)):
    if not db.query(Company.id).filter(Company.id == payload.company_id).first():
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")

    workplace = Workplace(**payload.model_dump())
    db.add(workplace)
    db.commit()
    db.refresh(workplace)
    return workplace


@app.get("/api/workers", response_model=list[WorkerRead])
def list_workers(db: Session = Depends(get_db)):
    return db.query(Worker).order_by(Worker.id.asc()).all()


@app.post("/api/workers", response_model=WorkerRead)
def create_worker(payload: WorkerCreate, db: Session = Depends(get_db)):
    if not db.query(Workplace.id).filter(Workplace.id == payload.workplace_id).first():
        raise HTTPException(status_code=404, detail="Local de trabalho não encontrado.")

    worker = Worker(**payload.model_dump())
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


@app.get("/api/standards", response_model=list[StandardRead])
def list_standards(db: Session = Depends(get_db)):
    return db.query(Standard).order_by(Standard.id.asc()).all()


@app.post("/api/standards", response_model=StandardRead)
def create_standard(payload: StandardCreate, db: Session = Depends(get_db)):
    standard = db.query(Standard).filter(Standard.name == payload.name).first()
    if standard:
        raise HTTPException(status_code=400, detail="Norma já cadastrada.")

    standard = Standard(**payload.model_dump())
    db.add(standard)
    db.commit()
    db.refresh(standard)
    return standard


@app.get("/api/chemicals", response_model=list[ChemicalRead])
def list_chemicals(db: Session = Depends(get_db)):
    return db.query(Chemical).order_by(Chemical.id.asc()).all()


@app.post("/api/chemicals", response_model=ChemicalRead)
def create_chemical(payload: ChemicalCreate, db: Session = Depends(get_db)):
    chemical = db.query(Chemical).filter(Chemical.name == payload.name).first()
    if chemical:
        raise HTTPException(status_code=400, detail="Substância já cadastrada.")

    chemical = Chemical(**payload.model_dump())
    db.add(chemical)
    db.commit()
    db.refresh(chemical)
    return chemical


@app.get("/api/exposure-limits", response_model=list[ExposureLimitRead])
def list_limits(db: Session = Depends(get_db)):
    return db.query(ExposureLimit).order_by(ExposureLimit.id.asc()).all()


@app.post("/api/exposure-limits", response_model=ExposureLimitRead)
def create_limit(payload: ExposureLimitCreate, db: Session = Depends(get_db)):
    if not db.query(Chemical.id).filter(Chemical.id == payload.chemical_id).first():
        raise HTTPException(status_code=404, detail="Substância não encontrada.")
    if not db.query(Standard.id).filter(Standard.id == payload.standard_id).first():
        raise HTTPException(status_code=404, detail="Norma não encontrada.")

    limit = ExposureLimit(**payload.model_dump())
    db.add(limit)
    db.commit()
    db.refresh(limit)
    return limit


@app.get("/api/assessments", response_model=list[AssessmentRead])
def list_assessments(db: Session = Depends(get_db)):
    return db.query(Assessment).order_by(Assessment.id.asc()).all()


@app.post("/api/assessments", response_model=AssessmentRead)
def create_assessment(payload: AssessmentCreate, db: Session = Depends(get_db)):
    if not db.query(Standard.id).filter(Standard.id == payload.standard_id).first():
        raise HTTPException(status_code=404, detail="Norma não encontrada.")
    if not db.query(Company.id).filter(Company.id == payload.company_id).first():
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")
    if payload.workplace_id and not db.query(Workplace.id).filter(Workplace.id == payload.workplace_id).first():
        raise HTTPException(status_code=404, detail="Local não encontrado.")

    assessment = Assessment(**payload.model_dump())
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def calculate_leq(levels: List[float]) -> float:
    if not levels:
        raise ValueError("No measurements provided.")
    energy_sum = sum(10 ** (level / 10) for level in levels)
    return 10 * math.log10(energy_sum / len(levels))


def noise_limit_by_standard(standard: str) -> float:
    return STANDARDS.get(standard, STANDARDS["ACGIH"])["noise_db"]


@app.post("/api/noise/calculate", response_model=NoiseResponse)
def calculate_noise(payload: NoiseRequest):
    if not payload.levels:
        raise HTTPException(status_code=400, detail="levels cannot be empty")

    leq = calculate_leq(payload.levels)
    limit_db = noise_limit_by_standard(payload.standard)
    exchange_rate = 3.0
    dose_percent = (payload.exposure_hours / 8.0) * (2 ** ((leq - limit_db) / exchange_rate)) * 100.0
    dose_percent = max(dose_percent, 0.0)
    exceeds_limit = leq > limit_db or dose_percent > 100.0

    interpretation = (
        "A exposição supera o limite recomendado para o padrão selecionado."
        if exceeds_limit
        else "A exposição encontra-se dentro do limite recomendado para o padrão selecionado."
    )

    return NoiseResponse(
        standard=payload.standard,
        leq=round(leq, 2),
        dose_percent=round(dose_percent, 2),
        limit_db=limit_db,
        exceeds_limit=exceeds_limit,
        interpretation=interpretation,
    )


@app.post("/api/chemicals/calculate", response_model=ChemicalResponse)
def calculate_chemicals(payload: ChemicalRequest):
    details: list[dict] = []
    ratios: list[float] = []

    for item in payload.items:
        if item.limit_value <= 0:
            raise HTTPException(status_code=400, detail=f"limit_value inválido para {item.substance}")
        ratio = item.concentration / item.limit_value
        ratios.append(ratio)
        details.append(
            {
                "substance": item.substance,
                "concentration": item.concentration,
                "limit_value": item.limit_value,
                "limit_type": item.limit_type,
                "ratio": round(ratio, 4),
                "exceeds": ratio > 1,
            }
        )

    sum_ratio = sum(ratios)
    max_ratio = max(ratios) if ratios else 0.0
    exceeds_limit = sum_ratio > 1.0 or max_ratio > 1.0

    return ChemicalResponse(
        standard=payload.standard,
        sum_ratio=round(sum_ratio, 4),
        max_ratio=round(max_ratio, 4),
        exceeds_limit=exceeds_limit,
        details=details,
    )


@app.post("/api/vibration/calculate", response_model=VibrationResponse)
def calculate_vibration(payload: VibrationRequest):
    if payload.exposure_hours <= 0:
        raise HTTPException(status_code=400, detail="exposure_hours deve ser maior que zero")

    standard_limits = STANDARDS.get(payload.standard, STANDARDS["ACGIH"])
    if payload.vibration_type == "HAND_ARM":
        limit_value = standard_limits["vibration_hand_arm"]
    else:
        limit_value = standard_limits["vibration_whole_body"]

    a8 = payload.acceleration * math.sqrt(payload.exposure_hours / 8.0)
    exceeds_limit = a8 > limit_value

    return VibrationResponse(
        standard=payload.standard,
        a8=round(a8, 3),
        limit_value=limit_value,
        exceeds_limit=exceeds_limit,
        interpretation=(
            "A vibração excede o limite de exposição recomendado."
            if exceeds_limit
            else "A vibração está dentro do limite recomendado para a exposição avaliada."
        ),
    )


@app.post("/api/heat/calculate", response_model=HeatResponse)
def calculate_heat(payload: HeatRequest):
    standard_limits = STANDARDS.get(payload.standard, STANDARDS["ACGIH"])
    allowable_limit = standard_limits["heat"][payload.workload]
    exceeds_limit = payload.wbgt > allowable_limit

    return HeatResponse(
        standard=payload.standard,
        wbgt=round(payload.wbgt, 2),
        allowable_limit=allowable_limit,
        exceeds_limit=exceeds_limit,
        interpretation=(
            "O valor de WBGT excede o limite recomendado para o tipo de esforço físico."
            if exceeds_limit
            else "O WBGT está dentro do limite recomendado para o esforço físico avaliado."
        ),
    )
