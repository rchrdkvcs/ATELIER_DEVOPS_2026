from __init__ import app


def test_home_page_returns_expected_content():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert "Bonjour tout le monde" in response.text


def test_exercices_page_returns_student_name():
    client = app.test_client()

    response = client.get("/exercices/")

    assert response.status_code == 200
    assert "Richard Kovacs" in response.text
