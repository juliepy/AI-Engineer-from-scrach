[English Version →](../../../en/projects/project-04-incremental-indexing/)

> 관련 강의: [강의 07. 에이전트를 위한 명확한 작업 경계 설정하기](./../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) · [강의 08. 기능 목록을 사용하여 에이전트가 하는 일을 제한하기](./../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
> 템플릿 파일: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# 프로젝트 04. 런타임 피드백을 사용하여 에이전트 동작 수정하기

## 해야 할 일

런타임 관찰 가능성(runtime observability, 시작 로그, 임포트/인덱싱 로그, 오류 상태)을 추가하고, 레이어 간 위반(cross-layer violation)을 방지하기 위한 아키텍처 제약(architecture constraints)을 도입합니다. 에이전트가 수정할 수 있도록 런타임 버그를 심어 둡니다.

에이전트는 로그(log)나 오류 출력이 없으면 내부 오류를 인식하기 어렵고, 존재하지 않는 기능도 "구현되었다"고 잘못 판단할 수 있습니다. 런타임 피드백 루프를 갖추면 에이전트가 실행 결과를 직접 관찰하고 동작을 즉시 수정할 수 있습니다.

두 번 실행합니다. 첫 번째는 로그나 제약 없이, 두 번째는 적절한 도구와 규칙(rules)을 갖춘 상태로 진행합니다.

## 저장소에 포함된 프로젝트 사용하기

저장소 경로: [`projects/project-04/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04)

| 디렉터리 | 내용 | 비교할 것 |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/starter) | Project 03 코드이며 진단 신호가 약합니다. 삽입된 indexing 결함이 큰 파일 chunking을 깨뜨릴 수 있고 architecture check script가 없습니다. | runtime 신호 없이 근본 원인을 찾는 데 걸리는 시간. |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/solution) | structured logger, architecture boundary docs/script, 수정된 chunking logic, [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/clean-state-checklist.md)가 있습니다. | logs와 boundary checks가 수정 속도와 안정성을 개선하는지. |

확인 파일: [`projects/project-04/solution/src/services/logger.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/logger.ts), [`projects/project-04/solution/scripts/check-architecture.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/scripts/check-architecture.sh), [`projects/project-04/solution/docs/ARCHITECTURE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/docs/ARCHITECTURE.md), [`projects/project-04/solution/src/services/indexing-service.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/indexing-service.ts).

## 도구

- Claude Code 또는 Codex
- Git
- Node.js + Electron

## 하네스 메커니즘

런타임 피드백 + 범위 제어 + 증분 인덱싱(incremental indexing)
