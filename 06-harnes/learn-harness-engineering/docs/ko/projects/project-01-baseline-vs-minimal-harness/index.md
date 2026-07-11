[English Version →](../../../en/projects/project-01-baseline-vs-minimal-harness/)

> 관련 강의: [강의 01. 강력한 모델이 곧 신뢰할 수 있는 실행을 의미하지는 않습니다](./../../lectures/lecture-01-why-capable-agents-still-fail/index.md) · [강의 02. 하네스가 실제로 의미하는 것](./../../lectures/lecture-02-what-a-harness-actually-is/index.md)
> 템플릿 파일: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# 프로젝트 01. 프롬프트 단독 vs. 규칙 우선(Rules-First): 차이는 얼마나 클까

## 해야 할 일

최소한의 Electron 지식 베이스 앱 쉘(shell)을 구축합니다. 왼쪽에 문서 목록이 있고, 오른쪽에 Q&A 패널이 있으며, 로컬 데이터 디렉터리가 포함된 창입니다. 작업 자체는 복잡하지 않습니다. 복잡한 것은 에이전트(agent)가 이 작업을 완료하도록 만드는 방법입니다.

두 번 실행합니다. 첫 번째: 프롬프트만 사용하고 사전 준비 없이 진행합니다. 두 번째: `AGENTS.md`, `init.sh`, `feature_list.json`을 저장소에 미리 배치한 상태로 진행합니다. 그런 다음 비교합니다.

이 코스 시나리오는 짧은 재탐색/준비 시간을 예로 들며, 고정된 측정 결과가 아닙니다.

에이전트에게 규칙(rule)과 초기화(initialization) 단서를 제공하면 작업 범위를 스스로 파악하고 불필요한 탐색을 줄일 수 있습니다. 이처럼 최소한의 하네스만으로도 에이전트의 출발점과 결과 품질이 크게 달라집니다.

## 도구

- Claude Code 또는 Codex (하나를 선택하여 두 번의 실행 모두 동일하게 사용)
- Git (브랜치 관리 및 비교)
- Node.js + Electron (프로젝트 스택)
- 타이머 (각 실행의 소요 시간 기록)

## 하네스 메커니즘

최소 하네스(minimal harness): `AGENTS.md` + `init.sh` + `feature_list.json`

## 저장소에 포함된 프로젝트 사용하기

저장소 경로: [`projects/project-01/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01)

| 디렉터리 | 무엇이 들어있나 | 어떻게 사용할까 / 무엇을 비교할까 |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/starter) | 약한 하네스 실행용. 작업 설명은 [`task-prompt.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/starter/task-prompt.md)만 있고 `AGENTS.md`나 `feature_list.json`은 없습니다. | 프롬프트만 에이전트에 주고, 추가 구조 없이 무엇을 완성하는지 측정합니다. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/solution) | 같은 제품 슬라이스에 명시적인 하네스 산출물 포함: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/CLAUDE.md), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/init.sh), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/feature_list.json), [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/claude-progress.md). | 규칙/검증이 같은 작업을 어떻게 구체화하고 검증 가능하게 만드는지 비교합니다. |

구체적인 4개 기능은 창 실행, 문서 목록, 질문 패널, 로컬 데이터 디렉터리 생성입니다. 각 기능의 기대 증거는 `solution/feature_list.json`을 확인하세요.
