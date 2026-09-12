# Codex 작업 난이도 라우팅

하위 에이전트를 생성하기 전에 작업 난이도를 먼저 분류한다.

| 난이도 | 적용 작업 | 에이전트 |
| --- | --- | --- |
| LOW | grep/search, 코드 위치 탐색, 문서 확인, 단순 수정 | Luna (`gpt-5.6-luna`) |
| MEDIUM | 일반 기능 구현, 테스트 작성, 리팩터링 | Terra (`gpt-5.6-terra`) |
| HIGH | 시스템 설계, 복잡한 버그 분석, 보안/동시성 문제, 최종 코드 리뷰 | Sol (`gpt-5.6-sol`) |

작업이 여러 범주에 걸치면 가장 높은 난이도를 적용한다. 분류 후 해당 에이전트 설정을 사용해 하위 에이전트를 생성한다.

에이전트 설정은 `.codex/agents/` 아래에 있다. 각 TOML 파일은 에이전트의
필수 메타데이터인 `name`, `description`, `developer_instructions`와 실행 모델을
선택하는 `model`을 사용한다. 작업 특성상 추론 강도를 고정해야 하는 경우에는
`model_reasoning_effort`도 함께 지정한다.
