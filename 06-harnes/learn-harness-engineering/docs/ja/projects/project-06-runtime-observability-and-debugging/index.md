[中文版本 →](../../../zh/projects/project-06-runtime-observability-and-debugging/)

> 関連講義: [講義 11. エージェントのランタイムを観測可能にする](./../../lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md) · [講義 12. すべてのセッション終了時にきれいな引き継ぎを残す](./../../lectures/lecture-12-why-every-session-must-leave-a-clean-state/index.md)
> テンプレートファイル: [templates/](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/ja/resources/templates/)

# プロジェクト 06. 完全なエージェント harness を構築する（総合課題）

## やること

これは総合プロジェクトです。最初の 5 つのプロジェクトで学んだすべてを組み合わせ、完全なベンチマークを実行し、その後クリーンアップを行って品質が維持可能かを検証します。

ドキュメントインポート、インデックス、引用付き Q&A、ランタイム観測性、読みやすく再開可能なリポジトリ状態を含む、固定された複数機能タスクセットを使います。まず弱い harness のベースラインで実行し、次に最も強い harness で実行し、その後クリーンアップして再実行します。最後に harness の ablation 実験を行い、コンポーネントを 1 つずつ外して、どれが本当に重要かを確認します。

## リポジトリ内のプロジェクトを使う

リポジトリ内のパス: [`projects/project-06/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06)

| ディレクトリ | 含まれるもの | 比較すること |
|------|------|------|
| [`starter/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/starter) | プロダクトはほぼ完成していますが、harness は意図的に弱められています。基本的な [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/starter/AGENTS.md) のみで、`feature_list.json`、`session-handoff.md`、clean-state checklist、benchmark/cleanup scripts はありません。 | 弱い harness baseline の手動観察。 |
| [`solution/`](https://github.com/walkinglabs/learn-harness-engineering/tree/main/projects/project-06/solution) | 完全な harness: [`AGENTS.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/AGENTS.md), [`CLAUDE.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/CLAUDE.md), [`feature_list.json`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/feature_list.json), [`init.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/init.sh), [`session-handoff.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/session-handoff.md), [`clean-state-checklist.md`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/clean-state-checklist.md), quality/evaluator docs, scripts。 | [`projects/project-06/solution/scripts/benchmark.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/benchmark.sh) と [`projects/project-06/solution/scripts/cleanup-scanner.sh`](https://github.com/walkinglabs/learn-harness-engineering/blob/main/projects/project-06/solution/scripts/cleanup-scanner.sh) を実行し、quality evidence を比較します。 |

## ツール

- Claude Code または Codex
- Git
- Node.js + Electron
- 品質ドキュメントテンプレート
- 評価ルーブリック
- 最初の 5 プロジェクトで積み上げたすべての harness コンポーネント

## Harness メカニズム

完全な harness: すべてのメカニズム + 観測性 + ablation study
