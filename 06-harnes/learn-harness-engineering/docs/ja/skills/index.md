# スキル

このディレクトリには、このコースに同梱されている AI エージェント用スキルが含まれています。スキルは、Claude Code、Codex、Cursor、Windsurf などの AI コーディングエージェントが読み込んで専門的な作業を行うための、自己完結したプロンプトテンプレートです。

## harness-creator

AI コーディングエージェント向けの本番級 harness engineering スキルです。指示、状態、検証、スコープ、セッションライフサイクルという 5 つの中核サブシステムを作成、評価、改善するのを助けます。

### できること

- **harness をゼロから作る** — AGENTS.md、機能リスト、検証ワークフロー
- **既存の harness を改善する** — 5 サブシステム評価と優先度付き改善案
- **セッション継続性を設計する** — メモリ永続化、進捗追跡、引き継ぎ手順
- **本番パターンを適用する** — メモリ、コンテキストエンジニアリング、ツール安全性、マルチエージェント協調

### クイックスタート

スキルファイルはリポジトリの [`skills/harness-creator/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/skills/harness-creator) にあります。

```bash
npx skills add walkinglabs/learn-harness-engineering --skill harness-creator
```

Claude Code で使う場合は、`harness-creator/` ディレクトリをプロジェクトのスキルパスにコピーするか、エージェントに SKILL.md を直接読ませます。

### 参考パターン

このスキルには 7 つの焦点化されたリファレンスがあります。

| パターン | 使う場面 |
|---------|----------|
| Memory Persistence | エージェントがセッション間で忘れてしまう |
| Skill Runtime | 再利用可能なワークフローをスキルとしてまとめる |
| Context Engineering | コンテキスト予算管理、必要時ロード |
| Tool Registry | ツール安全性、並行制御 |
| Multi-Agent Coordination | 並列化、専門化ワークフロー |
| Lifecycle & Bootstrap | フック、バックグラウンドタスク、初期化 |
| Gotchas | 見落としやすい 15 個の失敗モードと修正策 |

### テンプレート

このスキルには、すぐ使えるテンプレートが同梱されています。

- `agents.md` — 作業ルール付き AGENTS.md 雛形
- `feature-list.json` — JSON Schema と機能リスト例
- `init.sh` — 標準初期化スクリプト
- `progress.md` — セッション進捗ログテンプレート
- `session-handoff.md` — セッション引き継ぎテンプレート

### スクリプト

このスキルには、scaffold、検証、HTML 評価レポート、構造 benchmark レポート用の純粋な Node.js スクリプトも含まれています。

### このスキルの作り方

`harness-creator` は **skill-creator** 方法論で開発されています。これは Anthropic 公式のメタスキルで、エージェントスキルの作成、テスト、反復改善に使います。skill-creator は、評価ランナー、採点器、ベンチマークビューアを備えた、ドラフト → テスト → 評価 → 反復の構造化ワークフローを提供します。

- **skill-creator ソース**: [anthropics/skills — skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **Claude Code skills docs**: [anthropics/claude-code — plugin-dev/skills](https://github.com/anthropics/claude-code/tree/main/plugins/plugin-dev/skills)
