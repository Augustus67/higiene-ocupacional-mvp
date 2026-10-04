# FastAPI app for hygiene occupational MVP

from __future__ import annotations

import math
from typing import List, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.norms import STANDARDS, SUPPORTED_STANDARDS

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

    if exceeds_limit:
        interpretation = "A exposição supera o limite recomendado para o padrão selecionado."
    else:
        interpretation = "A exposição encontra-se dentro do limite recomendado para o padrão selecionado."

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

    interpretation = (
        "Há excesso em relação ao limite de exposição aplicado."
        if exceeds_limit
        else "A soma das exposições permanece dentro dos limites aplicáveis."
    )

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

    interpretation = (
        "A vibração excede o limite de exposição recomendado."
        if exceeds_limit
        else "A vibração está dentro do limite recomendado para a exposição avaliada."
    )

    return VibrationResponse(
        standard=payload.standard,
        a8=round(a8, 3),
        limit_value=limit_value,
        exceeds_limit=exceeds_limit,
        interpretation=interpretation,
    )


@app.post("/api/heat/calculate", response_model=HeatResponse)
def calculate_heat(payload: HeatRequest):
    standard_limits = STANDARDS.get(payload.standard, STANDARDS["ACGIH"])
    allowable_limit = standard_limits["heat"][payload.workload]
    exceeds_limit = payload.wbgt > allowable_limit

    interpretation = (
        "O valor de WBGT excede o limite recomendado para o tipo de esforço físico."
        if exceeds_limit
        else "O WBGT está dentro do limite recomendado para o esforço físico avaliado."
    )

    return HeatResponse(
        standard=payload.standard,
        wbgt=round(payload.wbgt, 2),
        allowable_limit=allowable_limit,
        exceeds_limit=exceeds_limit,
        interpretation=interpretation,
    )
