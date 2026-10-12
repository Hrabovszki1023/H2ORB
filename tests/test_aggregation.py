from datetime import UTC, datetime

from h2orb.domain.models import (
    Defect,
    ExecutionStatus,
    ScenarioExecution,
)
from h2orb.domain.models import TestKind as CaseKind
from h2orb.services.aggregation import aggregate, visible_details


def execution(
    *,
    scenario_id: int,
    test_case_id: int,
    status: ExecutionStatus,
    executed_at: datetime,
    test_kind: CaseKind = CaseKind.MANUAL,
    with_defect: bool = False,
) -> ScenarioExecution:
    defects = (Defect(defect_id=7, formatted_id="DF000007"),) if with_defect else ()
    return ScenarioExecution(
        scenario_id=scenario_id,
        scenario_name=f"Scenario {scenario_id}",
        test_case_id=test_case_id,
        test_case_name=f"Test {test_case_id}",
        test_kind=test_kind,
        status=status,
        executed_at=executed_at,
        defects=defects,
    )


def test_uses_latest_execution_within_each_scenario_without_cross_scenario_deduplication() -> None:
    older = datetime(2026, 1, 1, tzinfo=UTC)
    newer = datetime(2026, 1, 2, tzinfo=UTC)
    executions = [
        execution(
            scenario_id=1,
            test_case_id=10,
            status=ExecutionStatus.FAILED,
            executed_at=older,
        ),
        execution(
            scenario_id=1,
            test_case_id=10,
            status=ExecutionStatus.PASSED,
            executed_at=newer,
        ),
        execution(
            scenario_id=2,
            test_case_id=10,
            status=ExecutionStatus.FAILED,
            executed_at=newer,
            with_defect=True,
        ),
    ]

    totals = aggregate(executions)

    assert totals.overall.total == 2
    assert totals.overall.by_status[ExecutionStatus.PASSED] == 1
    assert totals.overall.by_status[ExecutionStatus.FAILED] == 1
    assert totals.overall.failed_with_defect == 1


def test_hiding_passed_details_does_not_change_totals() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    executions = [
        execution(
            scenario_id=1,
            test_case_id=1,
            status=ExecutionStatus.PASSED,
            executed_at=timestamp,
        ),
        execution(
            scenario_id=1,
            test_case_id=2,
            status=ExecutionStatus.FAILED,
            executed_at=timestamp,
        ),
    ]

    totals = aggregate(executions)
    details = visible_details(executions, show_passed=False)

    assert totals.overall.total == 2
    assert len(details) == 1
    assert details[0].status is ExecutionStatus.FAILED


def test_splits_manual_and_automated_totals() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    totals = aggregate(
        [
            execution(
                scenario_id=1,
                test_case_id=1,
                status=ExecutionStatus.PASSED,
                executed_at=timestamp,
                test_kind=CaseKind.MANUAL,
            ),
            execution(
                scenario_id=1,
                test_case_id=2,
                status=ExecutionStatus.FAILED,
                executed_at=timestamp,
                test_kind=CaseKind.AUTOMATED,
            ),
        ]
    )

    assert totals.manual.total == 1
    assert totals.automated.total == 1
