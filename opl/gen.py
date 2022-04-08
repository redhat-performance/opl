import random
import datetime
import base64
import json
import uuid
import string


def get_auth_header(account, user, org_id=None):
    if org_id:
        pass
    else:
        org_id = account

    data = {
        "identity": {
            "account_number": account,
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
    return base64.b64encode(json.dumps(data).encode('UTF-8'))


def gen_datetime(plus_hours=None):
    utc_now = datetime.datetime.now(tz=datetime.timezone.utc)
    if plus_hours is None:
        return utc_now.isoformat()
    else:
        add_hours = datetime.timedelta(hours=plus_hours)
        return (utc_now + add_hours).isoformat()


def gen_account():
    return str(random.randrange(1000000, 10000000))


def gen_uuid():
    return str(uuid.uuid4())


def gen_subscription_manager_id():
    return gen_uuid()


def gen_insights_id():
    return gen_uuid()


def gen_machine_id():
    return gen_uuid()


def gen_ipv4():
    data = [str(random.randint(1, 255)) for i in range(4)]
    return '.'.join(data)

def gen_ipv6():
    return f"{random.randrange(16**4):x}:{random.randrange(16**4):x}::{random.randrange(16**4):x}:{random.randrange(16**4):x}:{random.randrange(16**4):x}"

def gen_mac():
    data = ['%02x' % random.randrange(256) for i in range(6)]
    return ':'.join(data)


def gen_hostname():
    return ''.join(random.choices(string.ascii_lowercase, k=10)) \
        + '.example.com'


def gen_string(size=10):
    return ''.join(random.choice(string.printable) for i in range(size))
