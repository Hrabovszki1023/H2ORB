from __future__ import annotations

from typing import Any


def map_projects(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": int(project["Id"]),
            "name": str(project.get("Name") or f"Project {project['Id']}"),
            "hasSubfolders": bool(project.get("HasSubfolders")),
        }
        for project in payload.get("Projects") or []
        if not project.get("Archived", False)
    ]


def map_subfolders(payload: dict[str, Any]) -> list[dict[str, Any]]:
    folder_groups = payload.get("Subfolders") or []
    folders = folder_groups[0] if folder_groups else []
    return [
        {
            "id": int(folder["Id"]),
            "projectId": int(folder["ProjectId"]),
            "parentFolderId": int(folder.get("ParentFolderId", 0)),
            "name": str(folder.get("Name") or f"Folder {folder['Id']}"),
            "hasSubfolders": bool(folder.get("HasSubfolders")),
        }
        for folder in folders
    ]


def map_scenarios(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scenarios = []
    for item in items:
        location = item.get("Location") or {}
        scenarios.append(
            {
                "id": int(item["Id"]),
                "formattedId": str(item.get("FormattedId") or f"TS{item['Id']}"),
                "name": str(item.get("Name") or f"Test scenario {item['Id']}"),
                "folderId": location.get("FolderId"),
                "location": str(location.get("Text") or ""),
                "projectName": str(location.get("ProjectName") or ""),
                "path": [
                    {
                        "id": int(folder["Id"]),
                        "name": str(folder.get("Name") or f"Folder {folder['Id']}"),
                    }
                    for folder in location.get("Path") or []
                ],
                "hasExecutions": (
                    bool(item["HasExecutions"]) if "HasExecutions" in item else None
                ),
            }
        )
    return scenarios
