from h2orb.api.routes import health
from h2orb.main import create_app


def test_health_endpoint() -> None:
    assert health() == {"status": "ok"}


def test_required_routes_are_registered() -> None:
    app = create_app()

    assert str(app.url_path_for("index")) == "/"
    assert str(app.url_path_for("health")) == "/health"
    assert str(app.url_path_for("application_status")) == "/api/v1/status"
    assert str(app.url_path_for("aqua_scenarios", project_id=3)) == (
        "/api/v1/aqua/projects/3/scenarios"
    )
    assert str(app.url_path_for("aqua_report", project_id=3)) == (
        "/api/v1/aqua/projects/3/report"
    )
