# Apple 로그인 연동 가이드

Keycloak(realm `Sandori`)에 "Apple로 로그인"을 붙이는 운영 절차입니다. 2026-10-07 테스트 서버에 실제로 적용하면서 확인한 내용을 기준으로 씁니다. 설계 배경과 탈퇴(revoke) 연계는 별도 설계 문서에서 다룹니다.

## 구성 요약

```
브라우저 ──▶ Keycloak 로그인 화면 ──(Apple 버튼)──▶ appleid.apple.com
                                                         │ 사용자 인증
브라우저 ◀── 서비스로 복귀 ◀── Keycloak ◀──(form_post)───┘
                                /auth/realms/Sandori/broker/apple/endpoint
```

| 구성 요소 | 위치 |
|---|---|
| Apple IdP 확장 | `sandol_user_service/keycloak/providers/apple-identity-provider-1.16.0.jar` (klausbetz/apple-identity-provider-keycloak, Apache-2.0, LICENSE 동봉) |
| 마운트·기능 플래그 | 루트 `docker-compose.yml`의 `keycloak` 서비스: `/opt/keycloak/providers` 마운트, `KC_FEATURES: token-exchange,admin-fine-grained-authz:v1` |
| 로그인 버튼 | `sandol_user_service/web/keycloak-theme/sandori/login/` (`login.ftl`, `sandori-login.css`, `resources/img/apple-logo-white.svg`) |

확장 jar는 Keycloak 버전에 묶입니다. Keycloak 26.3.0~26.4.x는 1.15.0~1.16.0, 26.5.0 이상은 1.17.0 이상을 씁니다. Keycloak을 올릴 때 jar도 같이 바꿉니다.

## 1. Apple Developer 설정

[Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources)에서 합니다. 유료 Apple Developer Program 멤버십이 필요합니다.

### 1-1. Team ID 확인

[Membership details](https://developer.apple.com/account#MembershipDetailsCard)의 **Team ID**(10자)를 적어 둡니다. Keycloak의 Team ID 칸에 들어갑니다.

### 1-2. App ID (Primary)

1. Identifiers → `+` → **App IDs** → App
2. iOS 앱 Bundle ID로 만들고 Capabilities에서 **Sign in with Apple**을 켭니다.

웹 로그인만 쓸 때도 Services ID를 묶을 Primary App ID가 하나 필요합니다.

### 1-3. Services ID (Keycloak의 Client ID)

1. Identifiers → `+` → **Services IDs**
2. Identifier 예: `kr.sandori.auth` → 이 값이 Keycloak IdP의 **Client ID**입니다.
3. 만든 Services ID를 열고 **Sign in with Apple** 체크 → **Configure**
   - Primary App ID: 1-2의 App ID
   - **Domains and Subdomains**: 스킴 없이 도메인만. 예: `sandori.kr`, `<스테이징 도메인>`
   - **Return URLs**: 반드시 `https://`를 붙인 전체 URL. 예:
     - `https://sandori.kr/auth/realms/Sandori/broker/apple/endpoint`
     - `https://<스테이징 도메인>/auth/realms/Sandori/broker/apple/endpoint`
4. Done → Continue → **Save**

- Return URL에 `https://`를 빼면 "One or more Return URLs do not include a supported protocol…" 오류가 납니다.
- IP 주소와 `localhost`는 등록할 수 없습니다. HTTPS 도메인이 없는 로컬·개발 환경에서는 실제 Apple 로그인을 테스트할 수 없습니다.
- 경로의 `apple`은 Keycloak IdP의 Alias입니다. Alias를 바꾸면 Return URL도 바꿔야 합니다.
- 도메인 소유 확인 파일은 필요 없습니다.

### 1-4. Key (.p8)

1. Keys → `+` → 이름 입력, **Sign in with Apple** 체크 → **Configure** → Primary App ID 선택 → Save
2. Continue → Register → **Download**
   - `.p8` 파일은 **한 번만** 받을 수 있습니다. 잃어버리면 키를 새로 만들어야 합니다.
3. 키 상세 화면의 **Key ID**(10자)를 적어 둡니다.

`.p8`은 비밀값입니다. 채팅, 이슈, 저장소, 로그에 올리지 않습니다.

## 2. 서버 반영

루트 `docker-compose.yml`과 `sandol_user_service` 서브모듈에 이미 반영되어 있습니다. 서버에서는 최신 코드를 받은 뒤 Keycloak을 다시 만듭니다.

```bash
cd /root/tuk_sandol_team   # 운영 경로에 맞게
git pull && git submodule update --init sandol_user_service

# 테마 CSS·이미지가 바뀌었으면 gzip 캐시를 먼저 비운다(아래 주의 참고)
docker compose exec -T keycloak sh -c 'rm -rf /opt/keycloak/data/tmp/kc-gzip-cache/*' </dev/null

docker compose up -d --no-deps keycloak
docker compose logs keycloak | grep -i apple   # 확장 로드 확인
```

로드되면 `KC-SERVICES0047: apple (at.klausbetz.provider.AppleIdentityProviderFactory) is implementing the internal SPI social` 같은 WARN이 찍힙니다. 내부 SPI를 쓴다는 안내일 뿐 정상입니다.

주의:

- **재시작하면 진행 중인 로그인이 끊깁니다.** 인증 세션이 메모리에만 있어서, 재시작 전에 연 로그인 화면에서 넘어온 요청은 `cookie_not_found`(400)가 됩니다. 사용자가 적은 시간에 반영합니다.
- **테마 gzip 캐시.** Keycloak은 테마 정적 파일의 gzip 사본을 `/opt/keycloak/data/tmp/kc-gzip-cache`에 두고, 이 사본은 재시작해도 남습니다. 비우지 않으면 브라우저(gzip 요청)에는 옛 CSS가 나가고 curl(비압축)에는 새 CSS가 나와 반영 여부를 헷갈리게 됩니다.

## 3. Keycloak IdP 등록

관리 콘솔 → realm `Sandori` → **Identity providers** → **Apple**(확장이 추가한 항목)

| 설정 | 값 | 비고 |
|---|---|---|
| Alias | `apple` | Return URL 경로, `login.ftl`의 버튼 분기와 일치해야 함 |
| Client ID | Services ID (예: `kr.sandori.auth`) | App ID(Bundle ID)가 아님 |
| Client Secret | `.p8` 파일 내용 전체 | `-----BEGIN PRIVATE KEY-----`부터 `-----END PRIVATE KEY-----`까지 붙여 넣는다. 입력칸이 한 줄이라 줄바꿈이 빠져도 확장이 처리함(테스트 서버에서 확인) |
| Team ID | 1-1 값 | |
| Key ID | 1-4 값 | |
| Store Tokens | ON | 탈퇴 시 Apple 토큰 revoke에 필요 |
| Trust Email | OFF | 처음 로그인할 때 이메일 인증을 거침 |
| Sync Mode | `IMPORT` | 카카오 IdP와 동일 |
| Token-Exchange links existing accounts | **OFF** | 기본값이 ON. 켜면 이메일만으로 기존 계정에 자동 연결됨 |
| Hide on Login Page | OFF | |

확장은 로그인할 때마다 `.p8`로 client_secret(ES256 JWT)을 새로 만듭니다. 따로 JWT를 만들어 넣을 필요가 없습니다.

## 4. 로그인 버튼 (Apple HIG)

테마는 [Apple HIG: Sign in with Apple](https://developer.apple.com/design/human-interface-guidelines/sign-in-with-apple)의 커스텀 버튼 규칙을 따릅니다. 고칠 때 아래를 지킵니다.

- **문구**: Sign in / Sign up / Continue with Apple 셋 중 하나만 씁니다. 현재 값은 한국어 `Apple로 로그인`, 영어 `Sign in with Apple`입니다(`messages_*.properties`의 `socialLoginApple`).
- **로고**: [Apple Design Resources](https://developer.apple.com/design/resources/)의 공식 파일만 씁니다. 직접 그리거나 자르지 않습니다. 현재 파일은 Left-aligned, White, Small입니다.
- **색**: 흰 배경에서는 검정 버튼에 흰 로고·흰 글자를 씁니다. 로고와 글자 색은 같아야 합니다.
- **크기**: 로고 파일 높이를 버튼 높이와 같게 합니다(48px). 버튼은 다른 로그인 버튼보다 작으면 안 되고, 최소 140×30입니다.
- **글자 크기**: HIG의 "버튼 높이의 43%"는 영문 시스템 폰트 기준입니다. 한글은 같은 크기에서 더 커 보입니다. 그래서 Apple 공식 한국어 버튼(`appleid.cdn-apple.com/appleid/button?...&locale=ko_KR`)을 실측해, 글자 높이가 버튼의 약 0.28이 되는 18px로 맞췄습니다.

카카오 버튼은 [카카오 로그인 디자인 가이드](https://developers.kakao.com/docs/ko/kakaologin/design-guide)를 따릅니다. 문구는 `카카오 로그인`, 공식 말풍선 심볼, 배경 `#FEE500`, 글자 `#000` 85%입니다.

## 5. 검증

1. 서비스(예: `/meal-web/`) → 로그인 → **Apple로 로그인** → Apple 인증 → 처음이면 추가 정보 입력과 이메일 인증 → 서비스로 복귀
2. 관리 콘솔 → Users → 해당 사용자 → **Identity provider links**에 `apple`이 있는지 확인
3. "나의 이메일 가리기"를 고르면 `…@privaterelay.appleid.com` 주소로 계정이 만들어집니다. 이 주소로 메일을 보내려면 Apple Developer → Services → Sign in with Apple for Email Communication에 발신 도메인이나 주소를 등록해야 합니다.
4. 카카오 로그인이 계속 되는지 확인

## 6. 문제 해결

| 증상 | 원인 | 조치 |
|---|---|---|
| Apple 화면: `invalid_request` / "Invalid web redirect url." | 이 도메인의 Return URL이 Services ID에 등록되지 않음 | 1-3에 Return URL 추가 후 Save |
| Apple 화면: "문제가 발생했습니다. 다시 시도하십시오." / 토큰 교환 `invalid_client` | Client ID·Team ID·Key ID·`.p8` 불일치, 또는 **Apple 반영 지연** | 값을 다시 확인합니다. 테스트 서버에서는 값이 맞는데도 등록 직후 한동안 `invalid_client`가 났고, 시간이 지나 저절로 풀렸습니다. 설정 직후 실패하면 잠시 뒤 다시 시도합니다 |
| Keycloak: `IDENTITY_PROVIDER_LOGIN_ERROR error="cookie_not_found"` | Keycloak 재시작 등으로 인증 세션이 사라짐 | 탭을 닫고 서비스에서 로그인을 새로 시작 |
| 이메일 인증 후 서비스에서 "요청을 처리할 수 없어요"(400) | 서비스의 로그인 state가 만료됨. 식단 웹은 `MEAL_WEB_STATE_TTL_SECONDS` 기본 600초이고, 메일 인증에 10분 넘게 걸리면 발생 | 계정은 이미 만들어졌으므로 다시 로그인하면 됩니다. 서비스 쪽 개선은 별도 과제입니다 |
| 버튼 모양이 안 바뀜 | 테마 gzip 캐시 | 2절의 캐시 삭제 후 재시작 |
| 로그인 화면에 Apple 버튼이 없음 | 확장 미로드 또는 IdP 미등록·비활성 | `docker compose logs keycloak \| grep -i apple`, 관리 콘솔에서 IdP Enabled 확인 |

Keycloak 이벤트 로그는 `docker compose logs keycloak | grep -E 'IDENTITY_PROVIDER|LOGIN_ERROR'`로 봅니다. 토큰과 키 값은 로그나 문서에 옮겨 적지 않습니다.

## 되돌리기

1. 관리 콘솔에서 Apple IdP를 **Disabled**로 바꿉니다. IdP 설정이 남은 채 jar만 빼면 어떻게 동작하는지 확인하지 않았으니, 이 순서를 지킵니다.
2. 루트 `docker-compose.yml`에서 providers 마운트와 `KC_FEATURES` 줄을 지우고 `docker compose up -d --no-deps keycloak`을 실행합니다.
