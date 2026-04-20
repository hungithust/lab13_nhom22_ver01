from app.logging_config import scrub_event


def test_scrub_event_sanitizes_nested_strings() -> None:
    event = {
        "event": "request student@vinuni.edu.vn",
        "payload": {
            "message": "card 4111 1111 1111 1111",
            "items": ["call me at 0987654321"],
        },
    }

    out = scrub_event(None, "info", event)

    assert "student@" not in out["event"]
    assert "4111" not in out["payload"]["message"]
    assert "0987654321" not in out["payload"]["items"][0]
