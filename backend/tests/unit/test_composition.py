"""Tests for build_container() composition root."""
import pytest
from sqlmodel import Session, create_engine, SQLModel

from app.composition import build_container, Container
from app.application.pipeline import RunPipeline
from app.application.scoring import Scorer
from app.application.outreach import GenerateOutreach


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    import app.models  # noqa
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_build_container_returns_container(session):
    container = build_container(session)
    assert isinstance(container, Container)


def test_container_has_pipeline(session):
    container = build_container(session)
    assert isinstance(container.pipeline, RunPipeline)


def test_container_has_scorer(session):
    container = build_container(session)
    assert isinstance(container.scorer, Scorer)


def test_container_has_outreach(session):
    container = build_container(session)
    assert isinstance(container.outreach, GenerateOutreach)


def test_pipeline_run_returns_list_with_stub_adapters(session):
    """With stub adapters (empty pond), pipeline.run() returns empty list without crashing."""
    container = build_container(session)
    result = container.pipeline.run()
    assert isinstance(result, list)
    assert result == []  # stub _KboSource returns empty pond
