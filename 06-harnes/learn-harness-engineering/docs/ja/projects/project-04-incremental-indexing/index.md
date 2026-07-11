[中文版本 →](../../../zh/projects/project-04-incremental-indexing/)

> 関連講義: [講義 07. エージェントのタスク境界を明確に引く](./../../lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) · [講義 08. 機能リストでエージェントの作業を制約する](./../../lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md)
> テンプレートファイル: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/ja/resources/templates/)

# プロジェクト 04. ランタイムフィードバックでエージェントの挙動を修正する

## やること

起動ログ、インポート/インデックスログ、エラー状態などのランタイム観測性と、レイヤー越境を防ぐアーキテクチャ制約を追加します。さらに、エージェントに修正させるランタイムバグを仕込みます。

同じ作業を 2 回実行します。1 回目はログや制約なし。2 回目は適切なツールとルールを使います。

## リポジトリ内のプロジェクトを使う

リポジトリ内のパス: [`projects/project-04/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04)

| ディレクトリ | 含まれるもの | 比較すること |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/starter) | Project 03 のコードで診断シグナルが弱い状態です。仕込まれた indexing 欠陥により大きなファイルの chunking が壊れる可能性があり、architecture check script もありません。 | runtime シグナルなしで根本原因にたどり着く時間。 |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-04/solution) | structured logger、architecture boundary docs/script、修正済み chunking logic、[`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/clean-state-checklist.md) があります。 | logs と boundary checks が修正を速く、影響範囲を小さくするか。 |

確認するファイル: [`projects/project-04/solution/src/services/logger.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/logger.ts), [`projects/project-04/solution/scripts/check-architecture.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/scripts/check-architecture.sh), [`projects/project-04/solution/docs/ARCHITECTURE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/docs/ARCHITECTURE.md), [`projects/project-04/solution/src/services/indexing-service.ts`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-04/solution/src/services/indexing-service.ts).

## ツール

- Claude Code または Codex
- Git
- Node.js + Electron

## Harness メカニズム

ランタイムフィードバック + スコープ制御 + 増分インデックス
