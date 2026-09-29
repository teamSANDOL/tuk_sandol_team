from base64 import urlsafe_b64encode
from os import urandom
from secrets import token_hex, token_urlsafe


def main() -> None:
    print(f"SECRET_KEY={token_urlsafe(32)}")
    print(f"JWT_SECRET={token_urlsafe(32)}")
    print(f"RELAY_TO_CHATBOT_HMAC_SECRET={token_urlsafe(32)}")
    print(f"RELAY_CLIENT_SECRETS={token_urlsafe(32)}")
    print(f"KAKAO_TOKEN_ENCRYPTION_KEY={urlsafe_b64encode(urandom(32)).decode()}")
    print(f"KC_DB_PASSWORD={token_urlsafe(24)}")
    print(f"KEYCLOAK_ADMIN_PASSWORD={token_urlsafe(24)}")
    # 이 값은 URL과 SQL을 거치므로 특수 문자가 없는 hex 형식을 사용한다.
    print(f"PG_EXPORTER_PASSWORD={token_hex(24)}")


if __name__ == "__main__":
    main()
