[English Version →](../../../en/projects/project-05-grounded-qa-verification/)

> 관련 강의: [강의 09. 에이전트가 섣불리 완료를 선언하지 않도록 막기](./../../lectures/lecture-09-why-agents-declare-victory-too-early/index.md) · [강의 10. 완전한 파이프라인 실행만이 진정한 검증으로 인정됩니다](./../../lectures/lecture-10-why-end-to-end-testing-changes-results/index.md)
> 템플릿 파일: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/templates/)

# 프로젝트 05. 에이전트가 자신의 작업을 검증하도록 만들기

## 해야 할 일

역할 분리(role separation)를 구현합니다. 구현을 담당하는 생성자(generator), 검토를 담당하는 평가자(evaluator), 그리고 선택적으로 플래너(planner)를 만듭니다. 각 역할이 추가될 때마다 효과를 측정하기 위해 세 번 실행합니다.

에이전트가 구현과 검증을 동시에 담당하면 자신의 오류를 스스로 발견하기 어렵습니다. 독립된 평가자 역할을 분리하면 환각(hallucination)과 섣부른 완료 선언을 방지하고, 근거 기반(grounded) Q&A의 정확도를 높일 수 있습니다.

실질적인 기능 업그레이드(멀티턴 대화, 인용 패널 재설계, 또는 문서 필터링)를 선택하고 모든 실행에서 동일하게 유지합니다.

## 저장소에 포함된 프로젝트 사용하기

저장소 경로: [`projects/project-05/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05)

| 디렉터리 | 내용 | 비교할 것 |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/starter) | Project 04 기반 앱이며 대화 기록 업그레이드 전 상태입니다. | 세 변형을 다시 실행할 때의 시작점. |
| [`solution/single-role/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/single-role) | 한 에이전트가 계획, 구현, 자기 평가를 모두 수행합니다. | [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/single-role/evaluator-rubric.md)의 점수와 결함. |
| [`solution/gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/gen-eval) | generator + evaluator 구조이며 수정 증거가 있습니다. | [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/gen-eval/evaluator-rubric.md)의 점수와 revision notes. |
| [`solution/plan-gen-eval/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-05/solution/plan-gen-eval) | planner + generator + evaluator와 sprint contract가 있습니다. | [`sprint-contract.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/sprint-contract.md)와 [`evaluator-rubric.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-05/solution/plan-gen-eval/evaluator-rubric.md)의 높은 평가 증거. |

## 도구

- Claude Code 또는 Codex
- Git
- Node.js + Electron

## 하네스 메커니즘

자기 검증(self-verification) + 근거 기반 Q&A + 증거 기반 완료(evidence-based completion)
