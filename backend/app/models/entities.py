"""Database entities (SQLModel).

A Company is the spine. Each enrichment source hangs off it 1:1 or 1:N.
Score + OutreachAsset are produced by the pipeline and read by the web app.
JSON columns hold semi-structured detail (e.g. the per-criterion heatmap).
"""
from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship, Column, JSON


class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    enterprise_number: str = Field(index=True, unique=True)  # KBO ondernemingsnummer
    name: str
    region: str = "BE"
    nace_code: Optional[str] = None
    sector: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    zipcode: Optional[str] = Field(default=None, index=True)
    municipality: Optional[str] = None
    # Postal-code centroid (GeoNames); drives the area / radius filter + map.
    latitude: Optional[float] = Field(default=None, index=True)
    longitude: Optional[float] = Field(default=None, index=True)
    active: bool = True

    # pipeline status: pond -> filtered -> enriched -> scored
    stage: str = "pond"
    excluded: bool = False
    exclude_reason: Optional[str] = None

    financials: Optional["FinancialData"] = Relationship(back_populates="company")
    contacts: list["Contact"] = Relationship(back_populates="company")
    vacancies: list["Vacancy"] = Relationship(back_populates="company")
    tech: Optional["TechStack"] = Relationship(back_populates="company")
    score: Optional["Score"] = Relationship(back_populates="company")
    outreach: Optional["OutreachAsset"] = Relationship(back_populates="company")


class FinancialData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id", index=True)
    employees: Optional[int] = None         # FTE, from NBB social balance
    revenue: Optional[float] = None
    ebitda: Optional[float] = None
    fiscal_year: Optional[int] = None

    company: Optional[Company] = Relationship(back_populates="financials")


class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id", index=True)
    name: str
    title: Optional[str] = None             # CFO / CEO / Business-line director
    email: Optional[str] = None
    is_buyer_persona: bool = False

    company: Optional[Company] = Relationship(back_populates="contacts")


class Vacancy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id", index=True)
    title: str
    url: Optional[str] = None
    is_it_role: bool = False                # IT vacancy = buyer-intent signal

    company: Optional[Company] = Relationship(back_populates="vacancies")


class TechStack(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id", index=True)
    technologies: list = Field(default_factory=list, sa_column=Column(JSON))
    legacy_score: float = 0.0               # higher = more legacy = more AI impact

    company: Optional[Company] = Relationship(back_populates="tech")


class Score(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id", index=True, unique=True)
    total: float = 0.0
    rank: Optional[int] = None              # 1..N; top 10 = Rolling 10
    breakdown: dict = Field(default_factory=dict, sa_column=Column(JSON))  # heatmap
    contacted: bool = False                 # marking contacted rolls the next in

    company: Optional[Company] = Relationship(back_populates="score")


class OutreachAsset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id", index=True, unique=True)
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    teaser_title: Optional[str] = None
    teaser_preview: Optional[str] = None    # the first ~1.5 pages shown
    teaser_full: Optional[str] = None       # gated behind contact details

    company: Optional[Company] = Relationship(back_populates="outreach")


class Employee(SQLModel, table=True):
    """One of our own consultants — the source of a warm connection."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: Optional[str] = None
    title: Optional[str] = None             # current role at our firm
    active: bool = True

    connections: list["Connection"] = Relationship(back_populates="employee")


class Connection(SQLModel, table=True):
    """A warm tie from an employee to a company.

    type: EMPLOYER (worked there) | CLIENT (we delivered a project) |
          PERSONAL (knows someone who works there).
    end_date None = ongoing. A company with any CLIENT tie is treated as a client.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employee.id", index=True)
    company_id: int = Field(foreign_key="company.id", index=True)
    type: str = "EMPLOYER"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    note: Optional[str] = None              # e.g. PERSONAL "knows the CFO"

    employee: Optional["Employee"] = Relationship(back_populates="connections")
    company: Optional["Company"] = Relationship()


class SolutionCase(SQLModel, table=True):
    """WiiPlus solution-catalog reference cases — grounds the outreach LLM."""
    id: Optional[int] = Field(default=None, primary_key=True)
    sector: str = Field(index=True)
    title: str
    summary: str
    impact_metric: Optional[str] = None     # e.g. "+18% margin", "-30% manual work"


class WebsiteCrawl(SQLModel, table=True):
    """Cached Crawl4AI fetch of a company's website — so we crawl once, not per view."""
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id", index=True, unique=True)
    url: str                                 # normalised URL actually fetched
    markdown: Optional[str] = None           # the cache payload
    title: Optional[str] = None
    status: str = "ok"                       # ok | empty | error
    crawled_at: datetime = Field(default_factory=datetime.utcnow)


class CompanyBrief(SQLModel, table=True):
    """LLM-generated 'Why this company' brief, grounded in the website crawl + financials."""
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id", index=True, unique=True)
    why_company: list = Field(default_factory=list, sa_column=Column(JSON))  # [reason, ...]
    financial_summary: Optional[str] = None
    signals: list = Field(default_factory=list, sa_column=Column(JSON))      # [signal, ...]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
