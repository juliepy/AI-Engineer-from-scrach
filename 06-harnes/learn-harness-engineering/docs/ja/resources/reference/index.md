# 日本語リファレンス

これらのノートは、テンプレートを緩いファイルの集まりではなく、動作する harness として
使用する方法を説明します。

## 内部リファレンスノート

- [`method-map.md`](./method-map.md): 一般的な長時間実行の失敗モードを、最初に対処する成果物やポリシーにマッピング
- [`initializer-agent-playbook.md`](./initializer-agent-playbook.md): 機能作業が始まる前にイニシャライザーが残すべきもの
- [`coding-agent-startup-flow.md`](./coding-agent-startup-flow.md): 後のコーディング実行用の固定セッション開始フロー
- [`prompt-calibration.md`](./prompt-calibration.md): ルート指示を肥大化・脆弱化させずにシャープに保つ方法

## 主要記事

このリストは意図的に絞られています。Harness とはモデル周りの実行システムを意味します：エージェントループ、ツール実行、サンドボックス、状態、コンテキスト、検証、終了、オーケストレーション、オブザーバビリティです。

元の3つの記事がコースの骨格であり続けます：

- [OpenAI: Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (2026-02-11)
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (2025-11-26)
- [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24)

## 推奨読書順

1. `method-map.md`
2. `initializer-agent-playbook.md`
3. `coding-agent-startup-flow.md`
4. `prompt-calibration.md`
5. OpenAI Harness engineering
6. Anthropic Effective harnesses
7. Anthropic Harness design
