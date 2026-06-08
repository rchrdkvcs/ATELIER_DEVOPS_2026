import importlib.util
from pathlib import Path


def load_app():
    module_path = Path(__file__).resolve().parents[1] / "__init__.py"
    spec = importlib.util.spec_from_file_location("atelier_app", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


def test_home_page_returns_expected_content():
    app = load_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert "Bonjour tout le monde" in response.text


def test_exercices_page_returns_student_name():
    app = load_app()
    client = app.test_client()

    response = client.get("/exercices/")

    assert response.status_code == 200
    assert "Richard Kovacs" in response.text
