import hmac
import json
import time
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Dict
from urllib.parse import parse_qsl


class TelegramAuthError(Exception):
    pass


@dataclass
class TgUser:
    id: int
    raw: Dict[str, Any]


def verify_webapp_init_data(init_data: str, bot_token: str, max_age_seconds: int = 24 * 3600) -> TgUser:
    """
    Verifies Telegram WebApp initData signature.
    Returns TgUser if valid, otherwise raises TelegramAuthError.
    """
    if not init_data:
        raise TelegramAuthError("Missing initData")

    params = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = params.pop("hash", None)
    if not received_hash:
        raise TelegramAuthError("Missing hash in initData")

    auth_date_str = params.get("auth_date")
    if auth_date_str and auth_date_str.isdigit():
        auth_date = int(auth_date_str)
        if int(time.time()) - auth_date > max_age_seconds:
            raise TelegramAuthError("initData expired")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))

    secret_key = sha256(bot_token.encode("utf-8")).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise TelegramAuthError("Bad initData signature")

    user_json = params.get("user")
    if not user_json:
        raise TelegramAuthError("Missing user in initData")

    user_obj = json.loads(user_json)
    if "id" not in user_obj:
        raise TelegramAuthError("Missing user.id")

    return TgUser(id=int(user_obj["id"]), raw=user_obj)
