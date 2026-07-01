# Hotfix 배포 절차

이 문서는 운영 서버에서 특정 서비스 hotfix를 빠르게 반영할 때 사용합니다.
저장소 루트(`tuk_sandol_team`)에서 실행하는 것을 기준으로 합니다.

## 기본 원칙

- 먼저 상위 저장소를 최신화한 뒤, 필요한 submodule만 지정해서 업데이트합니다.
- DB 볼륨은 삭제하지 않습니다.
- hotfix 대상 서비스만 `--force-recreate`로 재생성합니다.
- 이미지 빌드가 필요한 서비스는 `--build`를 함께 사용합니다.
- 실행 전 `.env`와 서비스별 `.env`는 이미 운영 값으로 준비되어 있어야 합니다.

## Keycloak 테마 hotfix

`sandol_user_service/web/keycloak-theme` 변경만 반영하는 경우입니다.

```bash
git pull
git submodule update --init --recursive sandol_user_service
docker compose up -d --force-recreate keycloak
```

Keycloak 테마는 `docker-compose.yml`에서 다음 경로로 bind mount됩니다.

```text
./sandol_user_service/web/keycloak-theme:/opt/keycloak/themes:ro
```

따라서 테마 파일만 바뀐 경우에는 Keycloak 이미지를 다시 빌드할 필요가 없고,
컨테이너 재생성으로 변경된 파일을 다시 읽게 하면 됩니다.

## 특정 서비스 hotfix

서비스 코드가 submodule에 반영된 뒤 운영 서버에서 다음 패턴을 사용합니다.

```bash
git pull
git submodule update --init --recursive <submodule>
docker compose up -d --build --force-recreate <compose-service>
```

예시:

```bash
git pull
git submodule update --init --recursive sandol_kakao_bot_service
docker compose up -d --build --force-recreate kakao-bot-service
```

## 여러 서비스 hotfix

여러 submodule과 compose 서비스를 한 번에 반영할 수 있습니다.

```bash
git pull
git submodule update --init --recursive sandol_user_service sandol-auth-relay
docker compose up -d --build --force-recreate keycloak auth-relay
```

`keycloak`처럼 외부 이미지와 bind mount만 사용하는 서비스는 `--build` 영향이 거의 없지만,
직접 빌드하는 서비스와 함께 재생성할 때는 포함해도 됩니다.

## 전체 submodule 동기화

운영 서버의 모든 submodule을 상위 저장소에 고정된 commit으로 맞출 때 사용합니다.

```bash
git pull
git submodule update --init --recursive
```

이 명령은 submodule의 `main` 최신 commit을 임의로 따라가지 않고,
상위 저장소가 가리키는 commit으로 맞춥니다.

## 확인 명령

배포 후 컨테이너 상태와 로그를 확인합니다.

```bash
docker compose ps
docker compose logs --tail=100 keycloak
```

서비스별 로그 예시:

```bash
docker compose logs --tail=100 kakao-bot-service
docker compose logs --tail=100 auth-relay
```

## 주의사항

- `docker compose down -v`는 운영 DB와 Keycloak 데이터를 지울 수 있으므로 hotfix 배포에 사용하지 않습니다.
- submodule 내부에서 직접 `git pull origin main`을 실행하면 상위 저장소가 고정한 commit과 달라질 수 있습니다. 운영 배포는 `git submodule update --init --recursive <submodule>`을 우선 사용합니다.
- 상위 저장소에 submodule 포인터 commit이 반영되어 있어야 운영 서버가 같은 버전을 받을 수 있습니다.
