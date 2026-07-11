[中文版本 →](../../../zh/projects/project-01-baseline-vs-minimal-harness/)

> 関連講義: [講義 01. 強いモデルは信頼できる実行を意味しない](./../../lectures/lecture-01-why-capable-agents-still-fail/index.md) · [講義 02. harness とは何か](./../../lectures/lecture-02-what-a-harness-actually-is/index.md)
> テンプレートファイル: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/ja/resources/templates/)

# プロジェクト 01. プロンプトのみ vs ルール優先: どれほど差が出るか

## やること

最小限の Electron ナレッジベースアプリの外枠を作ります。左にドキュメント一覧、右に Q&A パネル、ローカルデータディレクトリを持つウィンドウです。タスク自体は複雑ではありません。複雑なのは、エージェントにどう完了させるかです。

同じ作業を 2 回実行します。1 回目は準備なしでプロンプトだけ。2 回目は `AGENTS.md`、`init.sh`、`feature_list.json` をあらかじめリポジトリに置いてから実行します。その後、結果を比較します。

このコース例は、短い再探索/準備の時間を例として使っており、固定の測定結果ではありません。

## ツール

- Claude Code または Codex（どちらかを選び、両方の実行で同じものを使う）
- Git（ブランチ管理と比較）
- Node.js + Electron（プロジェクトのスタック）
- タイマー（各実行時間を記録）

## Harness メカニズム

最小 harness: `AGENTS.md` + `init.sh` + `feature_list.json`

## リポジトリに同梱されたプロジェクトを使う

リポジトリ内のパス: [`projects/project-01/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01)

| ディレクトリ | 含まれるもの | 使い方 / 比較ポイント |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/starter) | 弱い harness の実行用。タスク説明は [`task-prompt.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/starter/task-prompt.md) のみで、`AGENTS.md` や `feature_list.json` はありません。 | prompt だけをエージェントに渡し、追加の構造なしで何が完了するか測定します。 |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-01/solution) | 同じプロダクトスライスに、明示的な harness 成果物を追加: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/AGENTS.md)、[`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/CLAUDE.md)、[`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/init.sh)、[`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/feature_list.json)、[`claude-progress.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-01/solution/claude-progress.md)。 | ルールと検証が同じタスクをどう具体化・検証可能にするか比較します。 |

具体的な4機能は「ウィンドウ起動」「ドキュメント一覧」「質問パネル」「ローカルデータディレクトリ作成」です。各機能の期待される証拠は `solution/feature_list.json` を参照してください。
