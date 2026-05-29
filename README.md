# TUK_산돌이

<p align="center"><img src="https://github.com/teamSANDOL/kpu_sandol_team/raw/main/img/logo_profile3.png?raw=true" width="300" height="300"></p>

산돌이는 한국공학대학교 학생과 학교 구성원이 사용하는 카카오톡 챗봇 서비스입니다.
이 저장소는 여러 서비스 저장소를 Git submodule로 묶어 운영하는 통합 레포이며, 현재 기준으로 Docker Compose 기반 MSA 운영 구조를 사용합니다.

## 빠른 시작

1. 저장소와 서브모듈을 준비합니다.

   ```bash
   git pull
   git submodule update --init --recursive
   ```

2. 루트 `.env.example`을 `.env`로 복사합니다.

   ```bash
   cp ./.env.example ./.env
   ```

3. 운영/배포 전이면 먼저 운영 문서를 확인합니다.

   - [운영 문서 인덱스](./docs/operations/README.md)
   - [환경 변수 체크리스트](./docs/operations/env-checklist.md)
   - [운영 데이터 디렉터리 준비 가이드](./docs/operations/production-data-setup.md)

4. 필요한 서비스별 `.env`를 준비하고, 전체 서비스를 실행합니다.

   ```bash
   docker compose up --build -d
   ```

## 문서 안내

- [문서 인덱스](./docs/README.md)
- [온보딩 문서](./docs/onboarding/README.md)
- [운영 문서](./docs/operations/README.md)
- [인증 문서](./docs/auth/README.md)

## 서비스별 문서

각 서브모듈의 상세 개발/실행 방법은 해당 서비스의 `README.md`를 기준으로 봅니다.

- [sandol_kakao_bot_service/README.md](./sandol_kakao_bot_service/README.md)
- [sandol_meal_service/README.md](./sandol_meal_service/README.md)
- [sandol-auth-relay/README.md](./sandol-auth-relay/README.md)
- [sandol-static-info-service/README.md](./sandol-static-info-service/README.md)
- [sandol_classroom_timetable_service/README.md](./sandol_classroom_timetable_service/README.md)
- [sandol_notice_notification/README.md](./sandol_notice_notification/README.md)
- [sandol-gateway/README.md](./sandol-gateway/README.md)
- [sandol_user_service/README.md](./sandol_user_service/README.md)
