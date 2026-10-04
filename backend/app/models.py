from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    cnpj = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sectors = relationship("Sector", back_populates="company")
    workplaces = relationship("Workplace", back_populates="company")


class Sector(Base):
    __tablename__ = "sectors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="sectors")
    workplaces = relationship("Workplace", back_populates="sector")


class Workplace(Base):
    __tablename__ = "workplaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="workplaces")
    sector = relationship("Sector", back_populates="workplaces")


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    role = Column(String(200), nullable=True)
    workplace_id = Column(Integer, ForeignKey("workplaces.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Standard(Base):
    __tablename__ = "standards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    limits = relationship("ExposureLimit", back_populates="standard")


class Chemical(Base):
    __tablename__ = "chemicals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    cas_number = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    limits = relationship("ExposureLimit", back_populates="chemical")


class ExposureLimit(Base):
    __tablename__ = "exposure_limits"

    id = Column(Integer, primary_key=True, index=True)
    chemical_id = Column(Integer, ForeignKey("chemicals.id"), nullable=False)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    limit_value = Column(Float, nullable=False)
    limit_type = Column(String(50), nullable=False, default="TWA")
    unit = Column(String(50), nullable=True, default="ppm")
    description = Column(Text, nullable=True)

    chemical = relationship("Chemical", back_populates="limits")
    standard = relationship("Standard", back_populates="limits")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    notes = Column(Text, nullable=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    workplace_id = Column(Integer, ForeignKey("workplaces.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    standard = relationship("Standard")
    company = relationship("Company")
    workplace = relationship("Workplace")
