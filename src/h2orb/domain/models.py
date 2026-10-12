from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class TestKind(StrEnum):
    MANUAL = "manual"
    AUTOMATED = "automated"


class ExecutionStatus(StrEnum):
    PASSED = "Passed"
    FAILED = "Failed"
    ABORTED = "Aborted"
    NOT_EXECUTED = "Not Executed"
    BLOCKED = "Blocked"
    NOT_COMPLETED = "Not Completed"
    NOT_APPLICABLE = "Not Applicable"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class Defect:
    defect_id: int | str
    formatted_id: str | None = None
    name: str | None = None
    url: str | None = None


@dataclass(frozen=True, slots=True)
class ScenarioExecution:
    scenario_id: int | str
    scenario_name: str
    test_case_id: int | str
    test_case_name: str
    test_kind: TestKind
    status: ExecutionStatus
    executed_at: datetime | None = None
    defects: tuple[Defect, ...] = ()
    scenario_url: str | None = None
    test_case_url: str | None = None

    @property
    def has_defect(self) -> bool:
        return bool(self.defects)

    @property
    def failure_class(self) -> str | None:
        if self.status is not ExecutionStatus.FAILED:
            return None
        return "F" if self.has_defect else "X"


@dataclass(slots=True)
class StatusTotals:
    total: int = 0
    by_status: dict[ExecutionStatus, int] = field(default_factory=dict)
    failed_with_defect: int = 0
    failed_without_defect: int = 0

    def add(self, execution: ScenarioExecution) -> None:
        self.total += 1
        self.by_status[execution.status] = self.by_status.get(execution.status, 0) + 1
        if execution.failure_class == "F":
            self.failed_with_defect += 1
        elif execution.failure_class == "X":
            self.failed_without_defect += 1

    def percentage(self, count: int) -> float:
        return round(count * 100 / self.total, 2) if self.total else 0.0


@dataclass(frozen=True, slots=True)
class ReportTotals:
    overall: StatusTotals
    manual: StatusTotals
    automated: StatusTotals
    by_scenario: dict[int | str, StatusTotals]
