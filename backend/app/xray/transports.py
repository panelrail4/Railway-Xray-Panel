COMPATIBILITY = {
    "raw": {"none": True, "tls": True, "reality": True},
    "xhttp": {"none": True, "tls": True, "reality": True},
    "websocket": {"none": True, "tls": True, "reality": False},
    "grpc": {"none": True, "tls": True, "reality": True},
    "httpupgrade": {"none": True, "tls": True, "reality": False},
}

def validate_combination(transport: str, security: str):
    transport = transport.lower()
    security = security.lower()
    if transport not in COMPATIBILITY:
        raise ValueError(f"Unsupported transport: {transport}")
    if security not in COMPATIBILITY[transport] or not COMPATIBILITY[transport][security]:
        raise ValueError(f"Unsupported combination: {transport} + {security}")
