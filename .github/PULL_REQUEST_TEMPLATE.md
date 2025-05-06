## 1. 개요
어떤 서비스(백엔드/프론트엔드)를 추가 또는 수정했는지 간단히 설명해주세요.

- 서비스명:
- 변경 요약:

---

## 2. 주요 변경 사항
- [ ] 필요 ENV 추가
  - [ ] .env.example 파일 수정
- [ ] Docker Compose 설정 추가
- [ ] Git Submodule 추가/수정
  - [ ] Git sumbodule의 branch를 main으로 설정
- [ ] [Gateway Repository](https://github.com/teamSANDOL/sandol-gateway]) 수정

---

## 3. 로컬 테스트 확인
- [ ] `docker compose up --build` 로 정상 실행 확인
  - [ ] gateway 서비스의 dependency에 추가된 서비스가 포함되어 있는지 확인
- [ ] 서비스 내부 기능 정상 작동 확인
- [ ] 의존 서비스 연결 확인 (DB, RabbitMQ 등)

---

## 4. 리뷰어가 확인해야 할 부분
- ex) Nginx proxy 설정 검토 필요
- ex) 환경변수 전달 방식 확인

---

## 5. 기타 참고 사항
- 관련 이슈:
- 관련 문서/링크:
