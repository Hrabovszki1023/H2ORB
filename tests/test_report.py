from h2orb.services.report import (
    _classify_failure,
    _count_statuses,
    _extract_defect_description,
    _extract_defects,
    _latest_by_test_job,
    _map_status,
    build_markdown_report,
    build_result_tree,
)


def test_builds_shared_folder_tree_and_aggregates_results() -> None:
    scenarios = [
        {
            "id": 67,
            "formattedId": "TS000067",
            "name": "Regressionstest",
            "projectName": "Demo Project",
            "path": [{"id": 10, "name": "Regression"}],
            "testCases": [
                {
                    "testJobId": 1,
                    "id": 60,
                    "formattedId": "TC000060",
                    "name": "Registrierung",
                    "status": "F",
                    "execution": {
                        "id": 49,
                        "formattedId": "TE000049",
                        "executedAt": "2023-06-20T14:55:01",
                        "executedAtText": "20.06.2023 14:55",
                    },
                    "defects": [
                        {
                            "id": 78,
                            "formattedId": "DF000078",
                            "name": "Benutzername vergeben",
                            "description": "Der Benutzername ist bereits vorhanden.",
                        }
                    ],
                }
            ],
        },
        {
            "id": 68,
            "formattedId": "TS000068",
            "name": "Akzeptanztest",
            "projectName": "Demo Project",
            "path": [{"id": 10, "name": "Regression"}],
            "testCases": [
                {
                    "testJobId": 2,
                    "id": 61,
                    "formattedId": "TC000061",
                    "name": "Anmeldung",
                    "status": "P",
                    "execution": None,
                    "defects": [],
                }
            ],
        },
    ]

    tree = build_result_tree(scenarios)

    assert tree is not None
    assert tree["name"] == "Demo Project"
    assert tree["totals"]["total"] == 2
    assert tree["totals"]["P"] == 1
    assert tree["totals"]["F"] == 1
    assert len(tree["children"]) == 1
    folder = tree["children"][0]
    assert folder["name"] == "Regression"
    assert len(folder["children"]) == 2
    assert folder["totals"] == tree["totals"]
    test_case = folder["children"][0]["children"][0]
    scenario = folder["children"][0]
    assert scenario["url"] == (
        "https://app.aqua-cloud.io/aquaWebNG/"
        "TestScenario/67?allowMultipleItemTabs=true"
    )
    assert test_case["url"] == (
        "https://app.aqua-cloud.io/aquaWebNG/"
        "TestCase/60?backUrl=%2FaquaWebNG%2FMain%2FNavigation"
    )
    assert [child["type"] for child in test_case["children"]] == [
        "execution",
        "defect",
    ]
    assert test_case["children"][0]["url"] == (
        "https://app.aqua-cloud.io/aquaWebNG/ViewExecution/49"
    )
    assert test_case["children"][1]["url"] == (
        "https://app.aqua-cloud.io/aquaWebNG/"
        "Defect/78?backUrl=%2FaquaWebNG%2FMain%2FNavigation"
    )
    assert test_case["children"][1]["description"] == (
        "Der Benutzername ist bereits vorhanden."
    )
    assert all(child["totals"] is None for child in test_case["children"])


def test_selected_folder_becomes_tree_root() -> None:
    scenarios = [
        {
            "id": 67,
            "formattedId": "TS000067",
            "name": "Regressionstest",
            "projectName": "Demo Project",
            "path": [
                {"id": 10, "name": "Tests"},
                {"id": 11, "name": "Regression"},
            ],
            "testCases": [],
        }
    ]

    tree = build_result_tree(scenarios, selected_folder_id=11)

    assert tree is not None
    assert tree["type"] == "folder"
    assert tree["id"] == 11
    assert tree["name"] == "Regression"


def test_groups_passed_test_cases_below_each_scenario() -> None:
    scenarios = [
        {
            "id": 67,
            "formattedId": "TS000067",
            "name": "Regressionstest",
            "projectName": "Demo Project",
            "path": [],
            "testCases": [
                {
                    "testJobId": 1,
                    "id": 60,
                    "formattedId": "TC000060",
                    "name": "Passed case",
                    "status": "P",
                    "execution": {
                        "id": 49,
                        "formattedId": "TE000049",
                        "executedAtText": "20.06.2023 14:55",
                    },
                    "defects": [],
                },
                {
                    "testJobId": 2,
                    "id": 61,
                    "formattedId": "TC000061",
                    "name": "Failed case",
                    "status": "N?",
                    "execution": None,
                    "defects": [],
                },
            ],
        }
    ]

    tree = build_result_tree(scenarios)

    assert tree is not None
    scenario = tree["children"][0]
    assert [child["type"] for child in scenario["children"]] == [
        "testCase",
        "passedGroup",
    ]
    failed_case, passed_group = scenario["children"]
    assert failed_case["formattedId"] == "TC000061"
    assert passed_group["name"] == "Passed"
    assert passed_group["totals"]["total"] == 1
    assert passed_group["totals"]["P"] == 1
    assert passed_group["children"][0]["formattedId"] == "TC000060"
    assert passed_group["children"][0]["children"][0]["formattedId"] == "TE000049"
    assert scenario["totals"]["total"] == 2
    assert scenario["totals"]["P"] == 1
    assert scenario["totals"]["N?"] == 1


def test_selects_latest_execution_per_test_job() -> None:
    executions = [
        {
            "Id": 1,
            "ExecutionDate": {"Value": "2026-01-01T10:00:00"},
            "TestScenarioInfo": {"TestJobId": 7},
        },
        {
            "Id": 2,
            "ExecutionDate": {"Value": "2026-01-02T10:00:00"},
            "TestScenarioInfo": {"TestJobId": 7},
        },
    ]

    assert _latest_by_test_job(executions)[7]["Id"] == 2


def test_maps_aqua_statuses() -> None:
    assert _map_status("Pass") == "P"
    assert _map_status("Failed") == "Failed"
    assert _map_status("NotRun") == "NE"
    assert _map_status("Queued") == "NE"
    assert _map_status("Waiting") == "NE"
    assert _map_status("Incomplete") == "NC"
    assert _map_status("InProgress") == "NC"


def test_classifies_failed_results_by_noise_marker() -> None:
    assert _classify_failure([], "[NOISE]") == "N?"
    assert _classify_failure([{"name": "[noise] Unstable environment"}], "[NOISE]") == "N"
    assert _classify_failure(
        [{"name": "[NOISE] Data"}, {"name": "Product defect"}], "[NOISE]"
    ) == "F"
    assert _classify_failure([{"name": "[NOISE] Data"}], "") == "F"


def test_failed_total_is_derived_from_failure_categories() -> None:
    totals = _count_statuses(["P", "F", "N", "N?", "NE"])

    assert totals["total"] == 5
    assert totals["X"] == 3
    assert totals["F"] == 1
    assert totals["N"] == 1
    assert totals["N?"] == 1


def test_extracts_only_viewable_aqua_defects() -> None:
    payload = {
        "Relations": [
            {
                "OtherItem": {"Id": 78, "FormattedId": "DF000078", "Type": "Defect"},
                "OtherItemCanView": "Granted",
            },
            {
                "OtherItem": {"Id": 52, "FormattedId": "RQ000052", "Type": "Requirement"},
                "OtherItemCanView": "Granted",
            },
        ]
    }

    assert _extract_defects(payload) == [
        {"id": 78, "formattedId": "DF000078", "name": ""}
    ]


def test_extracts_plain_text_from_defect_enclosures() -> None:
    payload = {
        "Enclosures": [
            {"Content": {"PlainText": "First paragraph", "Html": "<p>First</p>"}},
            {"Content": {"PlainText": "Second paragraph"}},
            {"Content": None},
        ]
    }

    assert _extract_defect_description(payload) == "First paragraph\n\nSecond paragraph"
    assert _extract_defect_description({"Enclosures": []}) is None


def test_builds_markdown_report_with_aqua_links_and_description() -> None:
    scenarios = [
        {
            "id": 67,
            "formattedId": "TS000067",
            "name": "Regressionstest",
            "projectName": "Demo Project",
            "path": [{"id": 10, "name": "Regression"}],
            "testCases": [
                {
                    "testJobId": 1,
                    "id": 60,
                    "formattedId": "TC000060",
                    "name": "Registrierung",
                    "status": "F",
                    "execution": {
                        "id": 49,
                        "formattedId": "TE000049",
                        "executedAtText": "20.06.2023 14:55",
                    },
                    "defects": [{
                        "id": 78,
                        "formattedId": "DF000078",
                        "name": "Benutzername vergeben",
                        "description": "Der Benutzername ist bereits vorhanden.",
                    }],
                }
            ],
        }
    ]
    tree = build_result_tree(scenarios)

    markdown = build_markdown_report(
        tree,
        generated_at="2026-10-11T12:00:00+00:00",
        language="de",
        summary_keys=["folder:10"],
    )

    assert "# AQUA-Testabschlussbericht" in markdown
    assert "| Demo Project | 1 | 0 | 1 | 1 | 0 | 0 |" in markdown
    assert "| Demo Project / Regression | 1 | 0 | 1 | 1 | 0 | 0 |" in markdown
    assert "[TS000067](https://app.aqua-cloud.io" in markdown
    assert ") — Regressionstest" in markdown
    assert "[TC000060](https://app.aqua-cloud.io" in markdown
    assert ") — Registrierung" in markdown
    assert "[TE000049](https://app.aqua-cloud.io" in markdown
    assert "[DF000078](https://app.aqua-cloud.io" in markdown
    assert "Der Benutzername ist bereits vorhanden." in markdown
    assert "**Status:** F" in markdown
