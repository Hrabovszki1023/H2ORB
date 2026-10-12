from __future__ import annotations

from collections.abc import Iterable

from h2orb.domain.models import (
    ReportTotals,
    ScenarioExecution,
    StatusTotals,
    TestKind,
)


def latest_scenario_executions(
    executions: Iterable[ScenarioExecution],
) -> list[ScenarioExecution]:
    """Return one latest execution per scenario/test-case occurrence.

    A test case used in two scenarios deliberately produces two result rows.
    """
    latest: dict[tuple[int | str, int | str], ScenarioExecution] = {}
    for execution in executions:
        key = (execution.scenario_id, execution.test_case_id)
        current = latest.get(key)
        if current is None or _is_newer(execution, current):
            latest[key] = execution
    return list(latest.values())


def aggregate(executions: Iterable[ScenarioExecution]) -> ReportTotals:
    overall = StatusTotals()
    manual = StatusTotals()
    automated = StatusTotals()
    by_scenario: dict[int | str, StatusTotals] = {}

    for execution in latest_scenario_executions(executions):
        overall.add(execution)
        by_scenario.setdefault(execution.scenario_id, StatusTotals()).add(execution)
        if execution.test_kind is TestKind.MANUAL:
            manual.add(execution)
        else:
            automated.add(execution)

    return ReportTotals(
        overall=overall,
        manual=manual,
        automated=automated,
        by_scenario=by_scenario,
    )


def visible_details(
    executions: Iterable[ScenarioExecution], *, show_passed: bool
) -> list[ScenarioExecution]:
    latest = latest_scenario_executions(executions)
    if show_passed:
        return latest
    return [execution for execution in latest if execution.status.value != "Passed"]


def _is_newer(candidate: ScenarioExecution, current: ScenarioExecution) -> bool:
    if candidate.executed_at is None:
        return False
    if current.executed_at is None:
        return True
    return candidate.executed_at > current.executed_at

