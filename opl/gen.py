import random
import datetime
import base64
import json
import uuid
import string


def get_auth_header(account, user):
    data = {
        "identity": {
            "account_number": account,
            "type": "User",
            "user": {
                "username": user,
                "email": user + "@example.com",
                "is_org_admin": True,
            },
            "internal": {
                "org_id": account,
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


def gen_hostname():
    return ''.join(random.choices(string.ascii_lowercase, k=10)) \
        + '.example.com'


def gen_string(size=10):
    return ''.join(random.choice(string.printable) for i in range(size))
