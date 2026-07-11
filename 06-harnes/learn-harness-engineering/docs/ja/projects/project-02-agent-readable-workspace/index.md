[中文版本 →](../../../zh/projects/project-02-agent-readable-workspace/)

> 関連講義: [講義 03. リポジトリを唯一の信頼できる情報源にする](./../../lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) · [講義 04. 指示を複数ファイルに分ける](./../../lectures/lecture-04-why-one-giant-instruction-file-fails/index.md)
> テンプレートファイル: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/ja/resources/templates/)

# プロジェクト 02. プロジェクトを読みやすくし、中断地点から再開できるようにする

## やること

新しいエージェントがプロジェクト構造、現在の進捗、次にやるべき作業をすばやく理解できるよう、リポジトリに「読みやすさ」を追加します。具体的には、ドキュメントのインポート、詳細表示、ローカル永続化を 2 セッションに分けて実装します。

同じ作業を 2 回実行します。1 回目は補助なし。2 回目は `ARCHITECTURE.md`、`PRODUCT.md`、`session-handoff.md` をあらかじめリポジトリに置いて実行します。

## リポジトリ内のプロジェクトを使う

リポジトリ内のパス: [`projects/project-02/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02)

| ディレクトリ | 含まれるもの | 比較すること |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/starter) | Project 01 のコードに、未完成のドキュメント import、詳細ビュー、永続化が入っています。ドキュメントはありますが薄く、`session-handoff.md` はありません。 | 2 回目のエージェントセッションがどれだけ再探索するか。 |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) | 同じプロダクト範囲が完成しており、[`projects/project-02/solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-02/solution) 配下に引き継ぎ用ドキュメント、[`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/feature_list.json)、[`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-02/solution/session-handoff.md) があります。 | 新しいセッションがリポジトリ状態だけで再開できるか。 |

## ツール

- Claude Code または Codex
- Git
- Node.js + Electron

## Harness メカニズム

エージェントが読めるワークスペース + 永続化された状態ファイル
