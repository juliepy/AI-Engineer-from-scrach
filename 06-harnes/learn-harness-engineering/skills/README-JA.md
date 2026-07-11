<p align="center">
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/English-d9d9d9"></a>
  <a href="README-CN.md"><img alt="简体中文" src="https://img.shields.io/badge/简体中文-d9d9d9"></a>
  <a href="README-ZH-TW.md"><img alt="繁體中文" src="https://img.shields.io/badge/繁體中文-d9d9d9"></a>
  <a href="README-JA.md"><img alt="日本語" src="https://img.shields.io/badge/日本語-d9d9d9"></a>
  <a href="README-ES.md"><img alt="Español" src="https://img.shields.io/badge/Español-d9d9d9"></a>
  <a href="README-FR.md"><img alt="Français" src="https://img.shields.io/badge/Français-d9d9d9"></a>
  <a href="README-KO.md"><img alt="한국어" src="https://img.shields.io/badge/한국어-d9d9d9"></a>
  <a href="README-AR.md"><img alt="العربية" src="https://img.shields.io/badge/العربية-d9d9d9"></a>
  <a href="README-VI.md"><img alt="Tiếng_Việt" src="https://img.shields.io/badge/Tiếng_Việt-d9d9d9"></a>
  <a href="README-DE.md"><img alt="Deutsch" src="https://img.shields.io/badge/Deutsch-d9d9d9"></a>
  <a href="README-TR.md"><img alt="Türkçe" src="https://img.shields.io/badge/Türkçe-d9d9d9"></a>
</p>

# Skills

このディレクトリには、Learn Harness Engineering プロジェクトで再利用できる AI agent skills が含まれています。各 skill は自己完結したプロンプトテンプレートで、Claude Code、Codex、Cursor、Windsurf などの AI コーディング agent が専門的な作業を行うために読み込めます。

## 利用可能な Skills

### harness-creator

AI コーディング agent 向けの本番品質 harness engineering skill です。AGENTS.md、機能リスト、検証ワークフロー、セッション継続メカニズムなどの agent harness ファイルの作成、評価、改善を支援します。

- **7 つの参照パターン**：Memory Persistence、Skill Runtime、Context Engineering、Tool Registry、Multi-Agent Coordination、Lifecycle & Bootstrap、Gotchas
- **テンプレート**：AGENTS.md/CLAUDE.md、feature-list.json、init.sh、progress.md、session-handoff.md
- **スクリプト**：scaffold、検証、HTML 評価レポート、構造 benchmark
- **10 個の組み込み eval テストケース**

詳細は [harness-creator/README.md](harness-creator/README.md) を参照してください。

## harness-creator の作成方法

`harness-creator` は **skill-creator** 方法論で作られました。これは Anthropic の公式 meta-skill で、agent skills を draft → test → evaluate → iterate の流れで作成、テスト、改善するためのものです。

## Skills の仕組み

各 skill は標準構造に従います。

1. **SKILL.md** — エントリーポイント。YAML frontmatter と agent への Markdown 指示を含みます。
2. **references/** — 必要に応じてコンテキストに読み込む追加ドキュメント。
3. **templates/** — skill が生成できる開始テンプレート。

Skills は progressive disclosure を使います。agent は最初に名前と説明だけを見て、トリガーされたときに SKILL.md 全体を読み込み、必要な場合だけ同梱リソースを読みます。

## セキュリティ

このディレクトリのファイルはセキュリティ確認済みです。

- バックドア、隠し URL、エンコードされた payload はありません
- データ流出やハードコードされた認証情報はありません
- コマンドインジェクション脆弱性はありません
- スクリプトは Node.js の組み込みモジュールのみを使用します
- 生成された `init.sh` は検出されたプロジェクト検証コマンドを実行します

## ライセンス

MIT
