"""Random data generators for performance testing."""

import base64
import datetime
import json
import random
import string
import uuid


def get_auth_header(account, user, org_id):
    """Build a base64-encoded cert-auth identity header."""
    data = {
        "identity": {
            "account_number": account,
            "auth_type": "cert-auth",
            "org_id": org_id,
            "type": "User",
            "user": {
                "username": user,
                "email": user + "@example.com",
                "is_org_admin": True,
            },
            "internal": {
                "org_id": org_id,
            },
            "system": {
                "cn": None,
            },
        }
    }
    return base64.b64encode(json.dumps(data).encode("UTF-8"))


def gen_datetime(plus_hours=None):
    """Return current UTC time (optionally shifted by hours) as ISO string."""
    utc_now = datetime.datetime.now(tz=datetime.timezone.utc)
    if plus_hours is None:
        return utc_now.isoformat()
    add_hours = datetime.timedelta(hours=plus_hours)
    return (utc_now + add_hours).isoformat()


def gen_account():
    """Generate a random 7-digit account number."""
    return str(random.randrange(1000000, 10000000))


def gen_uuid():
    """Generate a random UUID4 string."""
    return str(uuid.uuid4())


def gen_subscription_manager_id():
    """Generate a random subscription manager ID (UUID4)."""
    return gen_uuid()


def gen_insights_id():
    """Generate a random Insights ID (UUID4)."""
    return gen_uuid()


def gen_machine_id():
    """Generate a random machine ID (UUID4)."""
    return gen_uuid()


def gen_ipv4():
    """Generate a random IPv4 address."""
    data = [str(random.randint(1, 255)) for i in range(4)]
    return ".".join(data)


def gen_ipv6():
    """Generate a partial random IPv6 address."""
    return f"{random.randrange(16**4):x}:{random.randrange(16**4):x}::{random.randrange(16**4):x}:{random.randrange(16**4):x}:{random.randrange(16**4):x}"


def gen_mac():
    """Generate a random MAC address."""
    data = [f"{random.randrange(256):02x}" for i in range(6)]
    return ":".join(data)


def gen_hostname():
    """Generate a random hostname under example.com."""
    return "".join(random.choices(string.ascii_lowercase, k=25)) + ".example.com"


def gen_string(size=10):
    """Generate a random printable string of given size."""
    return "".join(random.choice(string.printable) for i in range(size))


def gen_safe_string(size=10):
    """Generate a random lowercase username-like string of given size."""
    # starting with "u" to specify it is a username
    return "u" + "".join(random.choice(string.ascii_lowercase) for _ in range(size - 1))
