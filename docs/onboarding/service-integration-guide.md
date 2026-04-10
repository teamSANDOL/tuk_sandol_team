# 산돌이 프로젝트 서비스 통합 가이드

이 문서는 `tuk_sandol_team` 레포지토리에 새 서비스를 통합할 때 필요한 최소 절차를 정리합니다.

아래 1~3번을 모두 완료한 뒤 Pull Request를 생성하세요.

> Gateway 설정 PR이 먼저 준비되어야 compose/submodule 통합 PR을 진행할 수 있습니다.


## **1. `docker-compose.yml`에 서비스 추가**

`docker-compose.yml` 파일에 본인이 만든 서비스의 설정을 다음과 같이 추가해 주세요.

예시: `your-service` 라는 이름의 백엔드 서버를 추가한다고 가정할 경우

```yaml
  your-service:
    container_name: sandol_your_service
    build: ./sandol_your_service
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - PYTHONUNBUFFERED=1
    volumes:
      - ./sandol_your_service:/app
    networks:
      - sandol_network
```

- `build` 경로는 실제 서비스 코드가 위치한 서브모듈 경로(Dockerfile의 경로)입니다.
- 필요에 따라 `depends_on`, `ports`, `volumes` 등을 자유롭게 추가하셔도 됩니다.

## **2. Git Submodule 추가**

서비스 코드를 `tuk_sandol_team` 레포에 연결하기 위해 ****Git Submodule(서브모듈)**** 을 등록합니다.

### **✅ 서브모듈이란?**

- 다른 Git 레포지토리를 현재 레포지토리 내부에 포함시키는 방법입니다.
- 산돌이 각 서비스는 독립적으로 버전 관리되며, 통합 레포에서 참조만 합니다.

### **✅ 작업 위치**

아래 명령어는 **`tuk_sandol_team` 레포지토리 최상단 디렉토리에서 실행**해야 합니다.

(예: `~/projects/tuk_sandol_team` 위치에서)

### **✅ 명령어 예시**

```bash
**git submodule add** <서비스 레포지토리 URL> ./<폴더명>
```

인자 설명:

- `<서비스 레포지토리 URL>`: GitHub에 있는 본인 서비스의 레포 주소
- `<폴더명>`: 해당 서비스가 저장될 로컬 폴더 경로 (예: `sandol_meal_service`)

예시:

```bash
git submodule add <https://github.com/teamSANDOL/sandol_meal_service> ./sandol_meal_service
```

**추가 후에는 반드시 다음 명령어도 실행해 주세요:** 코드 파일을 가져오는 명령어입니다.

```bash
git submodule update --init --recursive
```

- 서브모듈 전체 main 브랜치로 변경하는 법
    
    ```bash
    git submodule foreach 'git checkout main && git pull origin main'
    ```
    

## **3. Gateway(Nginx) Route 설정 추가**

본인의 서비스로 들어오는 요청을 Gateway에서 라우팅할 수 있도록 ****Nginx 설정 파일****을 작성해야 합니다.

### **✅ 작업 절차**

1. **sandol-gateway 레포지토리를 클론**합니다.

2. **`feature/add-(서비스명)-config`** 형식의 새 브랜치를 생성합니다.

3. 아래 경로에 설정 파일을 추가합니다:

`sandol-gateway/gateway/routes/`

4. 설정 템플릿 파일은 `template.conf.tmp`를 참고하세요.

5. 작성 후 간단한 PR을 생성합니다.

- 서비스명 정도만 있으면 충분합니다.

→ PR 제목 예시: `feat: add route config for meal-service`

### **✅ 설정 예시**

```bash
# /template 경로 전체를 template 서버에 프록시
location /template/ {
    proxy_pass http://template-service:80/template/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-User-ID $http_x_user_id;
    proxy_set_header Origin $http_origin;
}
```

- `location` 경로는 외부에서 접근할 URI
- `proxy_pass`는 docker-compose 내 서비스 이름과 포트를 기준으로 작성

### **⚠️ 주의**

- 이 Gateway 설정 PR이 올라간 이후에만,

`tuk_sandol_team` 레포로의 통합 PR이 승인될 수 있습니다.

## **PR 작성 시 유의사항**

- 위 1~3번 작업을 모두 완료하신 후 PR을 생성해 주세요.
- PR 템플릿에 따라 변경된 내용을 상세히 작성해 주세요.
- PR이 머지되면, 서버 배포 시 `docker compose up --build` 만으로 통합될 수 있어야 합니다.

궁금한 점이 있다면 디스코드 채널에 자유롭게 문의 주세요!
