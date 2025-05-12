# TUK_산돌이
<p align="center"><img src="https://github.com/teamSANDOL/kpu_sandol_team/raw/main/img/logo_profile3.png?raw=true" width="300" height="300"></p>

# 산돌이
- 산돌이는 학생들에게 편의 기능을 제공하기 위해 2021년 산돌팀을 구성한 이후 현재 누적 6200명의 학생 및 학교 관계자가 이용하는 카카오톡 챗봇 서비스입니다.
- 산돌이는 kakao-i 오픈빌더를 통해 제작되었으며, AWS Lambda를 이용한 서버리스 아키텍쳐를 활용하고 있습니다.

## Getting Start
- 아래 주소를 통해 산돌이를 시작하실 수 있습니다.
> [바로가기](https://pf.kakao.com/_pRxlZxb)
1. 바로가기 링크 접속
2. 우측 상단 플러스 친구 등록하기
3. 챗봇 채팅하기


## TUK_SANDOL_TEAM
- [초기 산돌팀 레포지토리 바로가기](https://github.com/teamSANDOL/kpu_sandol_team)

## 개발 참여 방법
다음과 같이 작성하면 됩니다:

---

## 개발 참여 방법
1. 레포지토리를 클론한 후 최신 코드를 가져옵니다.

   ```bash
   git pull
   ```

2. 서브모듈을 초기화하고 업데이트합니다.

   ```bash
   git submodule update --init --recursive
   ```

3. (선택) 모든 서브모듈을 `main` 브랜치로 전환하고 최신 커밋을 가져옵니다.

   ```bash
   git submodule foreach 'git checkout main && git pull origin main'
   ```

4. 각 서브모듈 디렉토리에 `.env.example` 파일이 존재하는 경우, `.env` 파일로 복사합니다.

   ```bash
   cp ./<submodule>/.env.example ./<submodule>/.env
   ```

5. 전체 서비스를 실행합니다.

   ```bash
   docker compose up --build -d
   ```

> ⚠️ `.env` 복사 단계는 서브모듈마다 반복해야 하며, 환경 설정은 서비스별로 확인 바랍니다.


### AUTHORS
