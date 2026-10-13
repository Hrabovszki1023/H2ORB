# Security roadmap

This document records the security work required before H2ORB is exposed as a shared server.
Running the current version locally on `127.0.0.1` remains the supported low-risk setup. Until the
items marked **P0** are complete, a shared deployment must additionally be protected by network
access controls and must not be reachable from the public Internet.

## P0 — required before shared server operation

### Per-user login and server-side AQUA sessions

- Add a login dialog for personal AQUA credentials.
- Send credentials only over HTTPS.
- Validate the credentials directly against AQUA.
- Discard the password immediately after token acquisition; never persist it in a file, database,
  browser storage, cookie, URL, report, or log.
- Store AQUA access and refresh tokens only in the server-side session.
- Replace the shared global AQUA client with a client bound to the authenticated H2ORB session.
- Give the browser only an opaque, cryptographically random session identifier in a cookie with
  `HttpOnly`, `Secure`, and `SameSite=Strict`.
- Use short session lifetimes and require a new login if token renewal is not possible.
- Implement logout so that the AQUA session is closed, server-side tokens are removed, and the
  browser cookie is deleted.
- Prevent session fixation and apply rate limiting to login attempts.
- Return generic authentication errors that do not disclose whether an account exists.

Acceptance criteria:

- An unauthenticated request to every AQUA-backed endpoint is rejected.
- Two simultaneous users cannot access each other's AQUA client, tokens, projects, or reports.
- No password or token is present in browser storage, application logs, generated reports,
  container configuration, or process startup arguments.
- Logout and session expiry make the former session identifier unusable.

### Remove centrally stored AQUA passwords

- Stop requiring `ARB_AQUA_USERNAME` and `ARB_AQUA_PASSWORD` for normal server operation.
- Remove the credentials from `compose.yaml` examples and deployment documentation once login is
  available.
- If a technical account mode remains available, make it an explicit restricted mode and document
  that secrets provided through container environment variables are visible to Docker
  administrators.

### Control packaged source contents

- Configure the source distribution with an explicit allow-list.
- Include only files required to build, install, document, and license H2ORB.
- Exclude local Word files, internal API references, caches, build output, `.env`, certificates,
  tokens, and other workstation artefacts.
- Inspect both the wheel and source archive in CI before publication.

Acceptance criteria:

- `python -m build` produces a wheel and source archive with a reviewed, deterministic file list.
- Neither archive contains `.env`, credentials, certificates, Swagger files, local office
  documents, caches, or internal host names.

## P1 — application hardening

### Validate and limit requests

- Replace untyped report request dictionaries with Pydantic request models.
- Define maximum request-body size, tree depth, collection sizes, field lengths, and report size.
- Apply timeouts and concurrency limits to expensive AQUA and report operations.
- Reject unexpected fields and invalid identifiers.

### Browser and HTTP protections

- Enable `TrustedHostMiddleware` with an explicit host allow-list.
- Add a restrictive Content Security Policy.
- Add `X-Content-Type-Options: nosniff`, an appropriate `Referrer-Policy`, and a restrictive
  `Permissions-Policy`.
- Enable HSTS at the HTTPS reverse proxy after HTTPS is deployed correctly.
- Disable or protect `/docs`, `/redoc`, and `/openapi.json` in production.
- Add CSRF protection to state-changing requests. This is mandatory before adding AQUA write
  operations.
- Continue accepting only `http` and `https` link schemes and validate generated AQUA URLs.

### Least privilege and confidentiality

- Document the minimum AQUA permissions required by each H2ORB feature.
- Keep H2ORB read-only until write operations have a separate threat model and authorization
  design.
- Treat test results, defects, descriptions, and generated reports as potentially confidential.
- Avoid logging request bodies, authorization headers, cookies, credentials, and AQUA tokens.

## P1 — repeatable security checks

Add the following gates to CI and fail publication on actionable findings:

- `pip-audit` for known Python dependency vulnerabilities;
- Bandit or Semgrep for Python static security analysis;
- Gitleaks for secrets in the repository and relevant Git history;
- CodeQL for repository-wide static analysis;
- CycloneDX or Syft to produce an SBOM for each release;
- Trivy or Grype to scan the final Docker image, including operating-system packages;
- an archive-content check for the wheel and source distribution.

Dependency versions used for a release must be reproducible through a reviewed constraints or lock
file. Docker base images and production images should use immutable digests or release-specific
tags where practical.

## P1 — dependency license compliance

Every released artefact must be checked for the licenses of both direct and transitive
dependencies. This includes Python packages, JavaScript packages if introduced later, bundled
browser or driver binaries, and operating-system packages in the Docker image.

- Maintain a reviewed allow-list of commonly accepted permissive licenses, initially including
  Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC, and PSF-2.0.
- Require manual review for weak-copyleft licenses such as MPL-2.0 and LGPL, because the applicable
  obligations depend on how the component is combined and distributed.
- Block publication on GPL, AGPL, SSPL, non-commercial, source-available, custom, missing, or
  unknown license metadata until the exact license text and usage have been reviewed and approved.
- Inspect the actual license files and `NOTICE` files rather than relying only on package
  classifiers or repository labels.
- Generate a versioned SBOM and a machine-readable license report for every release.
- Generate `THIRD_PARTY_NOTICES` from the reviewed dependency set and include it in distributed
  Docker images and other self-contained distributions.
- Preserve all attribution, copyright, license, and `NOTICE` requirements of included components.
- Re-run the check whenever a dependency, transitive dependency, base image, browser, or driver
  version changes.

Acceptance criteria:

- The release workflow has an explicit license-policy gate and fails on denied or unknown
  licenses.
- The report covers the complete dependency graph and the final Docker image, not only entries in
  `pyproject.toml`.
- Every dependency in the release SBOM has a reviewed license decision and traceable source URL.
- The shipped `THIRD_PARTY_NOTICES` matches the exact versions contained in the release.

Suitable tooling includes `pip-licenses` or ScanCode for Python license evidence, CycloneDX or Syft
for SBOM generation, and a container-level scanner for the final image. Tool output is evidence for
review, not a substitute for reviewing ambiguous or non-standard license terms.

## P2 — assurance and maintenance

- Create a lightweight threat model covering credentials, sessions, AQUA tokens, reports, reverse
  proxy boundaries, and future write operations.
- Review authentication and session handling against OWASP ASVS Level 2.
- Perform a focused penetration test after the login implementation and before wider deployment.
- Define a vulnerability-reporting process and add a repository `SECURITY.md` before a stable
  public release.
- Establish a dependency-update process, for example Dependabot or Renovate, with regular rebuilds
  and image scans.

## Current review baseline (2026-10-12)

- No obvious remote-code-execution, SQL-injection, path-traversal, or unsafe HTML-rendering issue was
  found in the reviewed code.
- Bandit reported no medium- or high-severity finding. Its single low-severity result was a false
  positive caused by the test-result status value `P`.
- `pip-audit` reported no known vulnerability in the installed H2ORB runtime dependencies. Findings
  in the development environment concerned the local `pip` and `pytest` tooling and do not replace
  a scan of the final Docker image.
- `.env` is not tracked by Git and was not present in the inspected wheel.
- The inspected source archive included more repository content than intended, including a local
  Word document. This is addressed by the P0 packaging task above.

Automated scans reduce risk but do not prove that an application is secure. The P0 design and its
acceptance tests remain prerequisites for operating H2ORB as a shared authenticated service.
