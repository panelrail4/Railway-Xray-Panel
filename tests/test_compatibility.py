from backend.app.xray.transports import validate_combination
def test_valid(): validate_combination("xhttp","reality")
def test_invalid():
    try: validate_combination("websocket","reality")
    except ValueError: return
    assert False
