from __future__ import annotations

import asyncio
from collections import Counter
from datetime import UTC, datetime
from typing import Any

from h2orb.aqua.client import AquaApiError, AquaClient

STATUS_ORDER = (
    "P",
    "F",
    "N",
    "N?",
    "A",
    "NE",
    "B",
    "NC",
    "NA",
    "?",
)


async def build_report(
    client: AquaClient,
    scenarios: list[dict[str, Any]],
    *,
    concurrency: int = 8,
    selected_folder_id: int = 0,
    aqua_web_base_url: str = "https://app.aqua-cloud.io/aquaWebNG",
    noise_marker: str = "[NOISE]",
) -> dict[str, Any]:
    semaphore = asyncio.Semaphore(concurrency)

    async def guarded(scenario: dict[str, Any]) -> dict[str, Any]:
        async with semaphore:
            return await _build_scenario(client, scenario, noise_marker=noise_marker)

    scenario_nodes = await asyncio.gather(*(guarded(scenario) for scenario in scenarios))
    await _enrich_defect_descriptions(client, scenario_nodes, concurrency=concurrency)
    tree = build_result_tree(
        scenario_nodes,
        selected_folder_id=selected_folder_id,
        aqua_web_base_url=aqua_web_base_url,
    )
    totals = tree["totals"] if tree else _count_statuses([])
    generated_at = datetime.now(UTC).isoformat()
    markdown = {
        language: build_markdown_report(tree, generated_at=generated_at, language=language)
        for language in ("de", "en")
    }
    return {
        "totals": totals,
        "scenarios": scenario_nodes,
        "tree": tree,
        "generatedAt": generated_at,
        "markdown": markdown,
    }


def build_result_tree(
    scenarios: list[dict[str, Any]],
    *,
    selected_folder_id: int = 0,
    aqua_web_base_url: str = "https://app.aqua-cloud.io/aquaWebNG",
) -> dict[str, Any] | None:
    """Build one expandable result tree and aggregate test results bottom-up."""
    if not scenarios:
        return None

    project_name = str(scenarios[0].get("projectName") or "Project")
    root = _tree_node("project", f"project:{project_name}", project_name)

    for scenario in scenarios:
        parent = root
        for folder in scenario.get("path") or []:
            folder_id = int(folder["id"])
            parent = _get_or_add_child(
                parent,
                _tree_node(
                    "folder",
                    f"folder:{folder_id}",
                    str(folder.get("name") or f"Folder {folder_id}"),
                    aqua_id=folder_id,
                ),
            )

        scenario_node = _tree_node(
            "scenario",
            f"scenario:{scenario['id']}",
            str(scenario.get("name") or ""),
            aqua_id=int(scenario["id"]),
            formatted_id=str(scenario.get("formattedId") or ""),
            url=_aqua_item_url(aqua_web_base_url, "scenario", int(scenario["id"])),
        )
        parent["children"].append(scenario_node)

        passed_group = _tree_node(
            "passedGroup",
            f"passed:{scenario['id']}",
            "Passed",
        )

        for test_case in scenario.get("testCases") or []:
            test_case_node = _tree_node(
                "testCase",
                f"test-case:{test_case['id']}:{test_case['testJobId']}",
                str(test_case.get("name") or ""),
                aqua_id=int(test_case["id"]),
                formatted_id=str(test_case.get("formattedId") or ""),
                totals=_count_statuses([test_case["status"]]),
                url=_aqua_item_url(aqua_web_base_url, "testCase", int(test_case["id"])),
            )
            if test_case["status"] == "P":
                passed_group["children"].append(test_case_node)
            else:
                scenario_node["children"].append(test_case_node)

            execution = test_case.get("execution")
            if execution:
                executed_at = execution.get("executedAtText") or execution.get("executedAt") or ""
                test_case_node["children"].append(
                    _tree_node(
                        "execution",
                        f"execution:{execution['id']}",
                        str(executed_at),
                        aqua_id=int(execution["id"]),
                        formatted_id=str(execution.get("formattedId") or ""),
                        url=_aqua_item_url(
                            aqua_web_base_url, "execution", int(execution["id"])
                        ),
                    )
                )

            for defect in test_case.get("defects") or []:
                test_case_node["children"].append(
                    _tree_node(
                        "defect",
                        f"defect:{defect['id']}",
                        str(defect.get("name") or ""),
                        aqua_id=int(defect["id"]),
                        formatted_id=str(defect.get("formattedId") or ""),
                        url=_aqua_item_url(aqua_web_base_url, "defect", int(defect["id"])),
                        description=defect.get("description"),
                    )
                )

        if passed_group["children"]:
            scenario_node["children"].append(passed_group)

    _aggregate_tree(root)
    if selected_folder_id:
        return _find_folder(root, selected_folder_id)
    return root


def _tree_node(
    node_type: str,
    key: str,
    name: str,
    *,
    aqua_id: int | None = None,
    formatted_id: str = "",
    totals: dict[str, int] | None = None,
    url: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    return {
        "type": node_type,
        "key": key,
        "id": aqua_id,
        "formattedId": formatted_id,
        "name": name,
        "url": url,
        "description": description,
        "totals": totals,
        "children": [],
    }


def _get_or_add_child(parent: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    for child in parent["children"]:
        if child["key"] == candidate["key"]:
            return child
    parent["children"].append(candidate)
    return candidate


def _aggregate_tree(node: dict[str, Any]) -> dict[str, int] | None:
    child_totals = []
    for child in node["children"]:
        totals = _aggregate_tree(child)
        if totals is not None:
            child_totals.append(totals)

    if node["type"] == "testCase":
        return node["totals"]
    if node["type"] in {"project", "folder", "scenario", "passedGroup"}:
        node["totals"] = _sum_totals(child_totals)
        return node["totals"]
    return None


def _aqua_item_url(base_url: str, item_type: str, item_id: int) -> str:
    base = base_url.rstrip("/")
    paths = {
        "scenario": f"TestScenario/{item_id}?allowMultipleItemTabs=true",
        "testCase": (
            f"TestCase/{item_id}?backUrl=%2FaquaWebNG%2FMain%2FNavigation"
        ),
        "execution": f"ViewExecution/{item_id}",
        "defect": f"Defect/{item_id}?backUrl=%2FaquaWebNG%2FMain%2FNavigation",
    }
    return f"{base}/{paths[item_type]}"


def _find_folder(node: dict[str, Any], folder_id: int) -> dict[str, Any] | None:
    if node["type"] == "folder" and node["id"] == folder_id:
        return node
    for child in node["children"]:
        found = _find_folder(child, folder_id)
        if found is not None:
            return found
    return None


async def _build_scenario(
    client: AquaClient, scenario: dict[str, Any], *, noise_marker: str
) -> dict[str, Any]:
    scenario_id = int(scenario["id"])
    jobs, executions = await asyncio.gather(
        client.get_test_jobs(scenario_id),
        client.get_all_scenario_executions(scenario_id),
    )
    latest_by_job = _latest_by_test_job(executions)
    rows = []
    for job in sorted(jobs, key=lambda item: int(item.get("Index", 0))):
        test_case = job.get("TestCaseInfo") or {}
        raw_execution = latest_by_job.get(int(job["Id"]))
        row = _test_case_row(job, test_case, raw_execution)
        if row["status"] == "Failed" and raw_execution is not None:
            if raw_execution.get("HasDefect"):
                relations = await client.get_execution_relations(int(raw_execution["Id"]))
                row["defects"] = _extract_defects(relations)
            row["status"] = _classify_failure(row["defects"], noise_marker)
        rows.append(row)

    totals = _count_statuses(row["status"] for row in rows)
    return {
        **scenario,
        "totals": totals,
        "testCases": rows,
    }


def _latest_by_test_job(executions: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    latest: dict[int, dict[str, Any]] = {}
    for execution in executions:
        scenario_info = execution.get("TestScenarioInfo") or {}
        job_id = scenario_info.get("TestJobId")
        if job_id is None:
            continue
        job_id = int(job_id)
        current = latest.get(job_id)
        if current is None or _execution_key(execution) > _execution_key(current):
            latest[job_id] = execution
    return latest


def _execution_key(execution: dict[str, Any]) -> tuple[str, int]:
    date = (execution.get("ExecutionDate") or {}).get("Value") or ""
    return str(date), int(execution.get("Id", 0))


def _test_case_row(
    job: dict[str, Any],
    test_case: dict[str, Any],
    execution: dict[str, Any] | None,
) -> dict[str, Any]:
    test_case_id = int(test_case["Id"])
    if execution is None:
        automated = test_case.get("SupportsAutomaticExecution") in {"Complete", "Partially"}
        return {
            "testJobId": int(job["Id"]),
            "id": test_case_id,
            "formattedId": f"TC{test_case_id:06d}",
            "name": str(test_case.get("Name") or f"Test case {test_case_id}"),
            "kind": "Automated" if automated else "Manual",
            "status": "NE",
            "execution": None,
            "defects": [],
        }

    status = _map_status(str(execution.get("Status") or ""))
    execution_date = execution.get("ExecutionDate") or {}
    return {
        "testJobId": int(job["Id"]),
        "id": test_case_id,
        "formattedId": str(execution.get("TestCaseFormattedId") or f"TC{test_case_id:06d}"),
        "name": str(test_case.get("Name") or execution.get("TestCaseName") or ""),
        "kind": str(execution.get("TestExecutionType") or "Unknown"),
        "status": status,
        "execution": {
            "id": int(execution["Id"]),
            "formattedId": str(execution.get("FormattedId") or f"TE{execution['Id']:06d}"),
            "executedAt": execution_date.get("Value"),
            "executedAtText": execution_date.get("Text"),
        },
        "defects": [],
    }


def _map_status(status: str) -> str:
    return {
        "Pass": "P",
        "Passed": "P",
        "Failed": "Failed",
        "Aborted": "A",
        "Blocked": "B",
        "NotRun": "NE",
        "Incomplete": "NC",
        "NotApplicable": "NA",
        "InProgress": "NC",
        "Queued": "NE",
        "Waiting": "NE",
    }.get(status, "?")


def _classify_failure(defects: list[dict[str, Any]], noise_marker: str) -> str:
    if not defects:
        return "N?"
    marker = noise_marker.strip().casefold()
    if marker and all(marker in defect.get("name", "").casefold() for defect in defects):
        return "N"
    return "F"


def _extract_defects(payload: dict[str, Any]) -> list[dict[str, Any]]:
    defects: dict[int, dict[str, Any]] = {}
    for relation in payload.get("Relations") or []:
        other = relation.get("OtherItem") or {}
        if other.get("Type") != "Defect" or relation.get("OtherItemCanView") != "Granted":
            continue
        defect_id = int(other["Id"])
        defects[defect_id] = {
            "id": defect_id,
            "formattedId": str(other.get("FormattedId") or f"DF{defect_id:06d}"),
            "name": str(other.get("Name") or ""),
        }
    return list(defects.values())


async def _enrich_defect_descriptions(
    client: AquaClient,
    scenarios: list[dict[str, Any]],
    *,
    concurrency: int,
) -> None:
    defects_by_id: dict[int, list[dict[str, Any]]] = {}
    for scenario in scenarios:
        for test_case in scenario.get("testCases") or []:
            if test_case.get("status") not in {"F", "N"}:
                continue
            for defect in test_case.get("defects") or []:
                defects_by_id.setdefault(int(defect["id"]), []).append(defect)

    semaphore = asyncio.Semaphore(concurrency)

    async def load(defect_id: int) -> tuple[int, str | None]:
        try:
            async with semaphore:
                payload = await client.get_defect(defect_id, with_enclosure=True)
            return defect_id, _extract_defect_description(payload)
        except AquaApiError:
            return defect_id, None

    details = await asyncio.gather(*(load(defect_id) for defect_id in defects_by_id))
    for defect_id, description in details:
        for defect in defects_by_id[defect_id]:
            defect["description"] = description


def _extract_defect_description(payload: dict[str, Any]) -> str | None:
    descriptions = []
    for enclosure in payload.get("Enclosures") or []:
        content = enclosure.get("Content") or {}
        plain_text = str(content.get("PlainText") or "").strip()
        if plain_text:
            descriptions.append(plain_text)
    return "\n\n".join(descriptions) or None


def build_markdown_report(
    tree: dict[str, Any] | None,
    *,
    generated_at: str,
    language: str = "de",
    summary_keys: list[str] | None = None,
) -> str:
    text = _REPORT_TEXT.get(language, _REPORT_TEXT["de"])
    if tree is None:
        return f"# {text['title']}\n\n{text['empty']}\n"

    selected_keys = set(summary_keys or [])
    summary_nodes = [(tree, tree["name"])]
    summary_nodes.extend([
        (node, path)
        for node, path in _nodes_with_paths(tree)
        if node is not tree
        and node["type"] == "folder"
        and node["key"] in selected_keys
    ])
    lines = [
        f"# {text['title']}",
        "",
        f"- **{text['start']}:** {_md_escape(tree['name'])}",
        f"- **{text['created']}:** {generated_at}",
        "",
        f"## {text['summary']}",
        "",
        f"| {text['area']} | SUM | P | X | F | N | N? | P% | X% | F% | N% | N?% |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for node, path in summary_nodes:
        totals = node["totals"]
        values = [str(totals[key]) for key in ("total", "P", "X", "F", "N", "N?")]
        rates = [
            _format_report_rate(totals[key], totals["total"], language)
            for key in ("P", "X", "F", "N", "N?")
        ]
        lines.append(f"| {_md_escape(path)} | " + " | ".join(values + rates) + " |")
    lines.extend([
        "",
        f"## {text['failed']}",
        "",
    ])

    failed_count = 0
    scenarios = list(_nodes_of_type(tree, "scenario"))
    for scenario in scenarios:
        failed_cases = [
            child for child in scenario["children"]
            if child["type"] == "testCase" and child["totals"]["X"] == 1
        ]
        if not failed_cases:
            continue
        failed_count += len(failed_cases)
        lines.extend([f"### {_md_node_heading(scenario)}", ""])
        for test_case in failed_cases:
            status_name = next(
                status for status in ("F", "N", "N?") if test_case["totals"][status]
            )
            lines.extend([
                f"#### {_md_node_heading(test_case)}",
                "",
                f"- **{text['status']}:** {status_name}",
            ])
            for child in test_case["children"]:
                if child["type"] == "execution":
                    lines.append(
                        f"- **{text['execution']}:** {_md_node_link(child)} — "
                        f"{_md_escape(child['name'])}"
                    )
                elif child["type"] == "defect":
                    lines.extend([
                        f"- **{text['defect']}:** {_md_node_link(child)} — "
                        f"{_md_escape(child['name'])}",
                        "",
                        f"> **{text['description']}:** "
                        f"{_md_quote(child.get('description') or text['unavailable'])}",
                    ])
            lines.append("")

    if not failed_count:
        lines.extend([text["no_failed"], ""])

    return "\n".join(lines)


def _nodes_of_type(node: dict[str, Any], node_type: str) -> Any:
    if node["type"] == node_type:
        yield node
    for child in node["children"]:
        yield from _nodes_of_type(child, node_type)


def _nodes_with_paths(
    node: dict[str, Any], parent_path: tuple[str, ...] = ()
) -> Any:
    path = parent_path
    if node["type"] in {"project", "folder"}:
        path = (*parent_path, node["name"])
    yield node, " / ".join(path)
    for child in node["children"]:
        yield from _nodes_with_paths(child, path)


def _format_report_rate(value: int, total: int, language: str) -> str:
    if not total:
        return "–"
    formatted = f"{value / total * 100:.1f}"
    if language == "de":
        formatted = formatted.replace(".", ",")
    return f"{formatted} %"


def _md_node_link(node: dict[str, Any]) -> str:
    label = node.get("formattedId") or node.get("name") or ""
    escaped = _md_escape(label)
    return f"[{escaped}]({node['url']})" if node.get("url") else escaped


def _md_node_heading(node: dict[str, Any]) -> str:
    link = _md_node_link(node)
    name = _md_escape(node.get("name"))
    return f"{link} — {name}" if node.get("formattedId") and name else link


def _md_escape(value: Any) -> str:
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )


def _md_quote(value: Any) -> str:
    return _md_escape(value).replace("\r", "").replace("\n", "  \n> ")


_REPORT_TEXT = {
    "de": {
        "title": "AQUA-Testabschlussbericht", "start": "Startordner", "created": "Erstellt",
        "summary": "Zusammenfassung", "area": "Bereich",
        "failed": "Fehlgeschlagene Tests", "status": "Status",
        "execution": "Ausführung", "defect": "AQUA-Defect", "description": "Beschreibung",
        "unavailable": "Nicht verfügbar", "no_failed": "Keine fehlgeschlagenen Tests.",
        "empty": "Keine Ergebnisse.",
    },
    "en": {
        "title": "AQUA Test Completion Report", "start": "Start folder", "created": "Created",
        "summary": "Summary", "area": "Area", "failed": "Failed tests", "status": "Status",
        "execution": "Execution", "defect": "AQUA defect", "description": "Description",
        "unavailable": "Not available", "no_failed": "No failed tests.",
        "empty": "No results.",
    },
}


def _count_statuses(statuses: Any) -> dict[str, int]:
    counts = Counter(statuses)
    result = {"total": sum(counts.values())}
    result.update({status: counts.get(status, 0) for status in STATUS_ORDER})
    result["X"] = result["F"] + result["N"] + result["N?"]
    return result


def _sum_totals(totals: Any) -> dict[str, int]:
    result = {"total": 0, **{status: 0 for status in STATUS_ORDER}}
    for total in totals:
        for key in result:
            result[key] += int(total.get(key, 0))
    result["X"] = result["F"] + result["N"] + result["N?"]
    return result
