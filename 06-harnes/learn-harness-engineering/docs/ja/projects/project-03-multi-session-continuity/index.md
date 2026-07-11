[中文版本 →](../../../zh/projects/project-03-multi-session-continuity/)

> 関連講義: [講義 05. セッションをまたいでコンテキストを保つ](./../../lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md) · [講義 06. すべてのエージェントセッション前に初期化する](./../../lectures/lecture-06-why-initialization-needs-its-own-phase/index.md)
> テンプレートファイル: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/ja/resources/templates/)

# プロジェクト 03. セッション再起動後もエージェントが作業を続けられるようにする

## やること

エージェントにスコープ制御と検証ゲートを追加します。ドキュメント分割、メタデータ抽出、インデックス進捗表示、引用付き Q&A フローを実装します。`feature_list.json` で機能状態を追跡し、一度に 1 機能だけ進め、検証証拠なしに `pass` とマークしないようにします。

同じ作業を 2 回実行します。1 回目は制約なし。2 回目は厳格なルールを適用します。

## リポジトリ内のプロジェクトを使う

リポジトリ内のパス: [`projects/project-03/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03)

| ディレクトリ | 含まれるもの | 比較すること |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/starter) | Project 02 のコードで、indexing と citation 付き Q&A がまだ未完成です。初期の [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/starter/feature_list.json) はありますが、最終的な handoff/restart 成果物はありません。 | 複数機能をまたぐときにエージェントが逸れたり状態を失ったりするか。 |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-03/solution) | chunking、metadata、index status、citation-based QA が完成し、[`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/init.sh)、[`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/session-handoff.md)、[`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/claude-progress.md)、[`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-03/solution/clean-state-checklist.md) もあります。 | 各機能が pass になる前に具体的な検証証拠を持つか。 |

## ツール

- Claude Code または Codex
- Git
- Node.js + Electron

## Harness メカニズム

進捗ログ + セッション引き継ぎ + 複数セッション継続性
