# OpenAI アドバンスト SOP

これらの SOP は、記事の運用パターンを、フォローまたは適応可能な
具体的な実行プレイブックに変換したものです。

## 含まれる SOP

- [`layered-domain-architecture.md`](./layered-domain-architecture.md):
  明示的なレイヤーと横断的関心事の境界を確立する
- [`encode-knowledge-into-repo.md`](./encode-knowledge-into-repo.md):
  目に見えないナレッジをチャット、ドキュメント、記憶からリポジトリ内のファイルに移動する
- [`observability-feedback-loop.md`](./observability-feedback-loop.md):
  エージェントにログ、メトリクス、トレース、再現可能なデバグループを提供する
- [`chrome-devtools-validation-loop.md`](./chrome-devtools-validation-loop.md):
  ブラウザ自動化とスナップショットを使用して、クリーンになるまで UI の動作を検証する

## 使用方法

1. 現在のボトルネックに合った SOP を選ぶ。
2. チェックリストを使用して、欠けている成果物やツールをセットアップする。
3. 結果として得られたルールを、コピーした `repo-template/` ドキュメントにエンコードする。
4. 繰り返しのレビューコメントをチェック、スクリプト、ガードレールに変換する。

これらは盲目的にフォローすることを意図したものではありません。
ハーネスをより読みやすく、強制可能で、再現可能にするためのものです。
