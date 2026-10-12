# AQUA REST API endpoint mapping

Source: `swagger.json`, API version **26.30.0.0**.

The supplied document differs from the initially expected version 26.29.0.0. The mapping below is
therefore based on 26.30.0.0 and must be checked against the installed AQUA instance during the
first integration test.

## Authentication

AQUA uses OAuth 2 password grant at `POST api/token`. Requests send the returned access token as a
Bearer token. Tokens expire after a few minutes. `DELETE api/Session` invalidates an active token
and releases its associated AQUA session/licence.

The initial client implementation uses one configured technical AQUA account and shares its
connection pool and token safely between concurrent web requests. User-specific AQUA identities can
later be introduced behind the same client interface.

## Read-only report workflow

| Purpose | AQUA operation |
| --- | --- |
| Projects and folder tree | `GET /api/Navigation/Tree` |
| Recursive scenario lookup | `GET /api/TestScenario/ItemList` with `includeSubfolders=true` |
| Test cases contained in a scenario | `GET /api/TestScenario/{id}/TestJob` |
| Scenario-specific executions | `GET /api/TestScenario/{id}/Execution` |
| Complete execution details | `GET /api/TestExecution/{id}` |
| Defect details | `GET /api/Defect/{id}` |
| Defect details including descriptions | `GET /api/Defect/{id}?withEnclosure=true` |

`ApiTestExecutionInfo.TestScenarioInfo` preserves the scenario context. This allows the application
to select the latest execution for each `(scenario id, test case id)` pair without incorrectly
deduplicating a test case across scenarios.

Manual and automated executions are distinguished exclusively through the standard AQUA field
`ApiTestExecutionInfo.TestExecutionType`, whose documented values are `Manual` and `Automated`.
H2ORB does not interpret company-specific fields, labels, workflows, or terms such as “manuell” and
“lauffähig”.

## Confirmed with real API responses

- Execution relations expose related defects as `ExecutionAffectedBy` relations whose
  `OtherItem.Type` is `Defect`.
- Only relations with `OtherItemCanView == Granted` are displayed.

## AQUA web links

The configurable `ARB_AQUA_WEB_BASE_URL` is combined with these confirmed paths:

| Item | Web path |
| --- | --- |
| Test scenario | `TestScenario/{id}?allowMultipleItemTabs=true` |
| Test case | `TestCase/{id}?backUrl=%2FaquaWebNG%2FMain%2FNavigation` |
| Test execution | `ViewExecution/{id}` |
| Defect | `Defect/{id}?backUrl=%2FaquaWebNG%2FMain%2FNavigation` |

H2ORB does not integrate Jira or resolve external defect relations. Failed executions link only to
their AQUA-internal formatted defect ID (`DFxxxxxx`). `F` means that a regular AQUA defect is
attached, `N` that all attached AQUA defects carry the configured noise marker, and `N?` that no
AQUA defect is attached. `X` is the derived total of all failed results: `X = F + N + N?`.

When `withEnclosure=true` is used, defect descriptions are available through
`Enclosures[].Content.PlainText` and `Enclosures[].Content.Html`. The Markdown report uses plain
text; AQUA HTML must not be rendered without sanitization.
