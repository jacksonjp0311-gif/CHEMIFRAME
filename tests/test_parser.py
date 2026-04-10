from chemiframe.intent.schema import default_intent, validate_intent


def test_default_intent_validates():
    result = validate_intent(default_intent())
    assert result["ok"] is True