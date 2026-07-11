# OpenAI アドバンストパック

このフォルダーは、OpenAI の「Harness engineering: leveraging Codex in an agent-first world」
記事で説明されている、よりオピニオネイトされたリポジトリ構造を
すぐにコピーできるスターターファイルとしてパッケージしたものです。

このパックは、最小限のハーネスではもう十分ではなく、リポジトリが次のものを
必要とする場合に使用してください:

- 短いルーティングスタイルの `AGENTS.md`
- リポジトリ内の持続的なシステム・オブ・レコードドキュメント
- アクティブおよび完了した実行計画
- 明示的なプロダクト、信頼性、セキュリティ、フロントエンドポリシーファイル
- プロダクトドメインとアーキテクチャレイヤーによる品質スコアリング
- モデルに適した参照資料フォルダー
- アーキテクチャ、ナレッジキャプチャ、ランタイム検証のための標準運用手順

## 含まれるスターターレイアウト

[`repo-template/`](./repo-template/index.md) 配下のスターターパックは、
以下の構造を反映しています:

```text
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   └── core-beliefs.md
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
│   ├── index.md
│   └── new-user-onboarding.md
├── references/
│   ├── design-system-reference-llms.txt
│   ├── nixpacks-llms.txt
│   └── uv-llms.txt
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

## 導入方法

1. リポジトリがまだ小規模な場合は、最小パックから始める。
2. より強固な構造が必要になったら、[`repo-template/`](./repo-template/index.md) の
   ファイルを自身のリポジトリにコピーする。
3. `AGENTS.md` は短く保つ。より深いドキュメントへのルーターとして扱い、
   百科事典としては扱わない。
4. 品質、信頼性、計画ドキュメントは、独立したクリーンアップの日ではなく、
   通常の作業の一部として更新する。
5. 生成された成果物と外部参照は明示的に保持し、エージェントが
   チャット履歴に頼らずに見つけられるようにする。

## SOP ライブラリ

[`sops/`](./sops/index.md) フォルダーは、記事の図を
ステップバイステップの運用手順に変換したものです:

- レイヤードドメインアーキテクチャのセットアップ
- 目に見えないナレッジをリポジトリにエンコード
- ローカルオブザーバビリティスタックとフィードバックループワークフロー
- UI作業のための Chrome DevTools 検証ループ

## 設計原則

- 短いエントリポイント、深くリンクされたドキュメント
- リポジトリをシステム・オブ・レコードとして扱う
- 機械的チェックは記憶されたルールに勝る
- 計画と品質履歴はコードの隣に置く
- クリーンアップと単純化は第一級の責務

このパックは意図的にオピニオネイトされていますが、盲目的にコピーするのではなく、
プロジェクトに合わせて適応させるべきです。
