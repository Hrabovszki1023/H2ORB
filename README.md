# H2ORB – H₂O Result Browser

A result browser and reporting tool for test-management data. The current integration analyses
AQUA test results through a server-side REST API proxy. Each user signs in with personal AQUA
credentials; direct communication with AQUA and the resulting tokens remain on the server.

H2ORB is an independent project and is not affiliated with or endorsed by any
test-management vendor.

Eine kompakte deutschsprachige Einführung mit Screenshots bietet die
[`H2ORB Kurzanleitung`](docs/kurzanleitung.md).

Normative behavior is documented separately: the
[`result tree contract`](docs/result-tree.md) defines status calculation and aggregation, the
[`report contract`](docs/report-contract.md) defines report contents, and the
[`security roadmap`](docs/security-roadmap.md) records security requirements and remaining work.

## Current state

This repository contains a locally runnable FastAPI application with an asynchronous AQUA
v26.30.0.0 REST client. Projects and folders can be selected in the browser and the application
loads the corresponding scenarios, test cases, latest executions, and AQUA defects through its
server-side proxy.

The domain layer already implements the central aggregation rules:

- every test case occurrence is evaluated in its own test scenario;
- only the latest execution within that scenario is considered;
- failed executions are classified as `F` (regular defect), `N` (defect marked as noise), or
  `N?` (not yet linked to a defect);
- `X` is the derived total of all failed results: `X = F + N + N?`;
- compact rates and aggregate totals are calculated bottom-up for every tree level.

Results are displayed in a compact German/English desktop interface as an expandable explorer tree.
Project and folder rows are followed by test
scenario (`TS`), test case (`TC`), execution (`TE`), and defect (`DF`) nodes. A test case contributes
exactly one result. Execution and defect detail rows do not contribute additional results. Counts
are aggregated bottom-up to scenarios, folders, and the selected project. See
[`docs/result-tree.md`](docs/result-tree.md) for the complete presentation and aggregation rules.
Passed test cases are grouped below each scenario, while an optional failure-focused view shows
only `F`, `N`, and `N?` results and automatically opens their containing paths.

The in-page report preview includes AQUA defect descriptions and links to scenarios, test cases,
executions, and defects. The same report can be downloaded as Markdown. Its complete contract is
specified in [`docs/report-contract.md`](docs/report-contract.md).

The manual/automated distinction uses AQUA's standard `TestExecutionType` values (`Manual` and
`Automated`). The application deliberately does not depend on company-specific fields, labels, or
workflow terminology.

## Screenshots

### Expandable result tree

The desktop-oriented result tree keeps paths, scenarios, test cases, executions, defects, status
counts, and rates visible in one compact view. Passed test cases are grouped separately below each
scenario.

![Expandable AQUA result tree](https://raw.githubusercontent.com/Hrabovszki1023/H2ORB/main/docs/images/result-tree.png)

### Failure-focused analysis

The `Nur X-Testfälle` filter hides successful and otherwise irrelevant results. The remaining
failures can be narrowed further to regular defects (`F`), confirmed noise (`N`), and unclassified
failure candidates (`N?`).

![Failure-focused result tree with F, N and N? filters](https://raw.githubusercontent.com/Hrabovszki1023/H2ORB/main/docs/images/failure-filter.png)

### Select report summary sections

Folder checkboxes select additional summary rows. The selected root folder is always included as
the highlighted overall result.

![Selecting folders for the report summary](https://raw.githubusercontent.com/Hrabovszki1023/H2ORB/main/docs/images/summary-selection.png)

### Test completion report

The report combines the selected summary rows with failed test details, latest executions, AQUA
defects, defect descriptions, and direct links back to AQUA. It can also be downloaded as Markdown.

![AQUA test completion report](https://raw.githubusercontent.com/Hrabovszki1023/H2ORB/main/docs/images/report-preview.png)

## Install from PyPI

Python 3.12 or newer is required:

```powershell
py -m pip install h2orb
h2orb
```

Open <http://127.0.0.1:8000> after configuring the required `ARB_` environment variables.

### Local workstation operation

For installations delivered to a workstation through PyPI, H2ORB is intended to listen only on
the loopback interface. The browser-to-H2ORB connection then remains on that computer and does not
cross the network. HTTP is acceptable for this strictly local setup:

```env
ARB_HOST=127.0.0.1
ARB_ENVIRONMENT=development
ARB_SESSION_COOKIE_SECURE=false
ARB_RELOAD=false
ARB_AQUA_BASE_URL=https://aqua.example.invalid
```

Do not change `ARB_HOST` to `0.0.0.0`, forward port `8000`, or create a firewall exception. The
outbound connection from H2ORB to AQUA remains protected by HTTPS and TLS verification. Local HTTP
does not protect against malicious software already running with the user's permissions; local
HTTPS would not remove that workstation-level risk either.

## Local setup

Python 3.12 or newer is required.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python -m h2orb
```

Open <http://127.0.0.1:8000>. API documentation is available at
<http://127.0.0.1:8000/docs>.

Configuration uses environment variables prefixed with `ARB_`. Do not commit `.env` or real AQUA
credentials.

## Authentication and secure deployment

H2ORB requests each user's personal AQUA credentials in a login dialog. The password is passed
directly to AQUA for token acquisition and is not retained by H2ORB. AQUA access and refresh tokens
are isolated in short-lived, in-memory server sessions; the browser receives only an opaque
`HttpOnly` session cookie. Logout and session expiration close the AQUA client and invalidate that
cookie.

- Run H2ORB only in a trusted internal network.
- Do not publish port `8000` directly on the Internet.
- For any shared deployment, terminate HTTPS at a reverse proxy and set
  `ARB_SESSION_COOKIE_SECURE=true`; production mode refuses to start without this setting.
- Restrict access additionally with firewall rules and grant AQUA users only the permissions they
  require.
- Keep `.env`, passwords, certificate keys, and access tokens outside the image and repository.
- Treat generated reports as potentially confidential test data.

The login endpoint is rate-limited and state-changing requests use a per-session CSRF token. HTTPS
remains a deployment responsibility; without it, credentials and cookies are not protected while
in transit. The remaining hardening tasks and acceptance criteria are maintained in the
[security roadmap](docs/security-roadmap.md).

## Docker

### Run the published image

After creating a local `.env` from `.env.example`, pull and run the public `linux/amd64` image:

```powershell
docker pull hrabovszki/h2orb:main
docker run --detach --name h2orb `
  --restart unless-stopped `
  --env-file .env `
  --env ARB_HOST=0.0.0.0 `
  --publish 8000:8000 `
  hrabovszki/h2orb:main
```

Use an immutable version or `sha-*` tag for reproducible deployments. The `main` tag tracks the
latest successful build from the main branch.

### Build locally

Build and start the local container with the existing `.env` configuration:

```powershell
docker compose up --build -d
docker compose ps
```

Open <http://127.0.0.1:8000>. Stop and remove the container with:

```powershell
docker compose down
```

The image runs as an unprivileged `h2orb` user, exposes port `8000`, and checks `/health`. The `.env`
file is excluded from the build context and is injected only when the container starts.

To test the AQUA connection from the built Linux image:

```powershell
docker compose run --rm h2orb python -m h2orb.check_connection
```

If AQUA uses an internal certificate authority, mount its PEM bundle read-only and configure the
path inside the container:

```yaml
services:
  h2orb:
    environment:
      ARB_AQUA_CA_BUNDLE: /certificates/company-ca.pem
    volumes:
      - ./certificates/company-ca.pem:/certificates/company-ca.pem:ro
```

TLS verification remains enabled. Do not add certificates, `.env`, passwords, or access tokens to
the image.

### Publish from Gitea to Docker Hub

Gitea Actions verifies the Python project inside a Python 3.12 Docker build stage, then publishes the tested
`linux/amd64` image as `hrabovszki/h2orb`. Configure these repository secrets in
Gitea before running `.gitea/workflows/docker-publish.yaml`:

- `DOCKERHUB_USERNAME`: Docker Hub account name
- `DOCKERHUB_TOKEN`: Docker Hub personal access token with read, write, and delete permissions

A push to `main` publishes the moving `main` tag and an immutable `sha-*` tag. A tag such as
`v0.1.0` publishes `0.1.0`, `0.1`, `0`, and `latest`. Prerelease tags never move `latest`.
After a successful image push, the workflow also synchronizes this README and the short description
to the Docker Hub overview page.

Never store the Docker Hub password or token in Git. Use a scoped access token instead of the
account password.

## License

H2ORB is open-source software licensed under the
[Apache License 2.0](LICENSE).

## Development checks

```powershell
ruff check .
pytest
python tools/check_dependency_licenses.py
```

The dependency license policy is defined in `tools/license-policy.toml`. The check follows the
complete installed H2ORB runtime dependency tree and fails on unknown, denied, or not explicitly
reviewed licenses. Docker builds additionally generate `THIRD_PARTY_NOTICES.md` and preserve the
packaged license files under `third-party-licenses/` inside the image.

## Project structure

```text
src/h2orb/
├── api/          # HTTP routes exposed to the browser
├── aqua/         # AQUA REST API adapter
├── domain/       # framework-independent models and rules
├── services/     # application use cases
├── static/       # browser assets
└── templates/    # server-rendered HTML
```

Place the reviewed Swagger reference under `docs/aqua-api/`. Check it for internal host names,
credentials, tokens, or other sensitive information before committing it.

The current endpoint mapping is documented in `docs/aqua-api/endpoint-mapping.md`.
