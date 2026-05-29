# 운영 문서 인덱스

이 디렉터리는 운영 환경 준비, 배포 전 점검, 운영 데이터 관리에 필요한 문서를 모아둡니다.

## 문서 구성

1. [환경 변수 체크리스트](./env-checklist.md)
2. [Docker Compose 체크리스트](./docker-compose-checklist.md)
3. [Keycloak 체크리스트](./keycloak-checklist.md)
4. [운영 데이터 디렉터리 준비 가이드](./production-data-setup.md)

## 권장 순서

1. `env-checklist.md`
2. `production-data-setup.md`
3. `docker-compose-checklist.md`
4. `keycloak-checklist.md`

## 운영 보조 스크립트

- [`scripts/generate_secrets.py`](../../scripts/generate_secrets.py): 루트 `.env`와 서비스 `.env`에 넣을 시크릿 생성 보조 스크립트
