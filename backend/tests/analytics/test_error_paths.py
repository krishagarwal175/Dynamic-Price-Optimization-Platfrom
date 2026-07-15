"""Error-path coverage for the analytics service (empty data, missing category)."""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationError
from app.pricing.optimization import Objective
from app.services.analytics import AnalyticsService
from tests.support import make_business_db


def _service() -> tuple[Session, AnalyticsService]:
    _, factory = make_business_db()
    session = factory()
    return session, AnalyticsService(session)


@pytest.mark.integration
def test_category_financials_missing_category_raises_not_found() -> None:
    _, service = _service()
    with pytest.raises(NotFoundError):
        service.category_financials(99999)


@pytest.mark.integration
def test_dataset_optimization_without_data_raises_validation() -> None:
    _, service = _service()
    with pytest.raises(ValidationError):
        service.dataset_optimization(objective=Objective.MAXIMIZE_REVENUE)


@pytest.mark.integration
def test_dataset_simulation_without_data_raises_validation() -> None:
    _, service = _service()
    with pytest.raises(ValidationError):
        service.dataset_simulation(objective=Objective.MAXIMIZE_REVENUE)


@pytest.mark.integration
def test_dataset_report_without_data_raises_validation() -> None:
    _, service = _service()
    with pytest.raises(ValidationError):
        service.dataset_report(objective=Objective.MAXIMIZE_REVENUE)
