from h2orb.services.navigation import map_projects, map_scenarios, map_subfolders


def test_maps_active_projects() -> None:
    payload = {
        "Projects": [
            {"Id": 7, "Name": "Active", "HasSubfolders": True, "Archived": False},
            {"Id": 8, "Name": "Archived", "HasSubfolders": False, "Archived": True},
        ]
    }

    assert map_projects(payload) == [
        {"id": 7, "name": "Active", "hasSubfolders": True}
    ]


def test_maps_first_requested_folder_group() -> None:
    payload = {
        "Subfolders": [
            [
                {
                    "Id": 11,
                    "ProjectId": 7,
                    "ParentFolderId": 0,
                    "Name": "Tests",
                    "HasSubfolders": True,
                }
            ]
        ]
    }

    assert map_subfolders(payload) == [
        {
            "id": 11,
            "projectId": 7,
            "parentFolderId": 0,
            "name": "Tests",
            "hasSubfolders": True,
        }
    ]


def test_maps_scenarios() -> None:
    items = [
        {
            "Id": 42,
            "FormattedId": "TS000042",
            "Name": "Regression",
            "HasExecutions": True,
            "Location": {
                "ProjectName": "Demo",
                "FolderId": 11,
                "Text": "Demo/Tests",
                "Path": [{"Id": 11, "Name": "Tests"}],
            },
        }
    ]

    assert map_scenarios(items) == [
        {
            "id": 42,
            "formattedId": "TS000042",
            "name": "Regression",
            "folderId": 11,
            "location": "Demo/Tests",
            "projectName": "Demo",
            "path": [{"id": 11, "name": "Tests"}],
            "hasExecutions": True,
        }
    ]


def test_missing_execution_flag_remains_unknown() -> None:
    scenarios = map_scenarios([{"Id": 42, "FormattedId": "TS000042", "Name": "Regression"}])

    assert scenarios[0]["hasExecutions"] is None
