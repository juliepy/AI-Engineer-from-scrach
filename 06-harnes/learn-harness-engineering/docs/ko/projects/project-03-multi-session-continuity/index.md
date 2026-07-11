[English Version →](../../../en/projects/project-03-multi-session-continuity/)

> 관련 강의: [강의 05. 세션 간에 컨텍스트를 유지하기](./../../lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md) · [강의 06. 모든 에이전트 세션 전에 초기화하기](./../../lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
> 템플릿 파일: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# 프로젝트 03. 세션 재시작 후에도 에이전트가 계속 작업하도록 만들기

## 해야 할 일

에이전트(agent)에 범위 제어(scope control)와 검증 게이트(verification gates)를 추가합니다. 문서 청킹(chunking), 메타데이터 추출, 인덱싱 진행 상태 표시, 인용 기반 Q&A 흐름을 구현합니다. `feature_list.json`을 사용하여 기능 상태를 추적합니다. 한 번에 하나의 기능만 처리하고, 검증 증거 없이는 "완료(pass)"로 표시할 수 없습니다.

장시간 실행되는 작업은 컨텍스트(context) 초기화나 중단으로 인해 연속성(continuity)을 잃기 쉽습니다. 진행 로그(progress log)와 세션 핸드오프를 결합하면 에이전트가 이전에 완료한 항목을 재확인하지 않고 정확한 다음 단계에서 재개할 수 있습니다.

두 번 실행합니다. 첫 번째는 제약 없이, 두 번째는 엄격한 적용 방식으로 진행합니다.

## 저장소에 포함된 프로젝트 사용하기

저장소 경로: [`projects/project-03/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03)

| 디렉터리 | 내용 | 비교할 것 |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/starter) | Project 02 코드에서 indexing과 citation 기반 Q&A가 아직 미완성입니다. 초기 [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/starter/feature_list.json)은 있지만 최종 handoff/restart 산출물은 없습니다. | 여러 기능 사이에서 에이전트가 drift하거나 재시작 후 상태를 잃는지. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/solution) | chunking, metadata, index status, citation-based QA가 완성되어 있고 [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/session-handoff.md), [`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/claude-progress.md), [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/clean-state-checklist.md)가 있습니다. | 각 기능이 pass로 표시되기 전에 구체적 검증 증거가 있는지. |

## 도구

- Claude Code 또는 Codex
- Git
- Node.js + Electron

## 하네스 메커니즘

진행 로그 + 세션 핸드오프 + 멀티 세션 연속성(multi-session continuity)
