# AGENTS.md

## Project
入力データを SPSS Modeler でベースライン自動モデル(.str)化し、以後反復改善する案件で使う Agent 指示書。主スキルは [.bob/skills/spss-modeler-baseline-automodel/](.bob/skills/spss-modeler-baseline-automodel/)(配置されている場合)。

## Commands
- `mcp__spss-clemb-mcp__execute_clemb` — Jython 実行。`script_file` と `log_file` は必須(`log_file` 省略するとログが残らない)
- `mcp__ibm-docs-mcp__search_ibm_docs` / `get_ibm_topic` — SPSS Modeler ノード仕様の裏取り
- PMML サマリ補助スクリプトはスキル配下 `_shared/scripts/` を使う(必要時、`uv run python` 経由で呼ぶ)

## Architecture
- `inputs/` (または `input/raw/`) — 入力データ配置先。文字コード(UTF-8 / MS932 / Shift_JIS 等)は要判定
- `.bob/skills/<skill-name>/` — 利用するスキル本体(SKILL.md / templates / _shared / フェーズ別ガイド)
- [.bob/mcp.json](.bob/mcp.json) — MCP 接続定義(spss-clemb-mcp / ibm-docs)。`<path-to-...>` プレースホルダーを自環境のパスに書き換えてから使う
- `runs/run_XXX/` — 試行ごとの成果物。標準サブ構成は `scripts/` `streams/` `outputs/` `pmml/` `logs/` `reports/`

## Rules
- **IMPORTANT**: 「データを見て」「分析して」「モデル作って」「予測して」等の曖昧依頼は、すべて **SPSS Modeler ストリーム生成 + .str 保存** 案件として扱う
- **NEVER**: pandas / numpy / scikit-learn / matplotlib で主分析を完結させる(列名確認等の補助用途のみ可)
- **NEVER**: ノードタイプ・プロパティ名・許容値を推測で書く。不明点は `mcp__ibm-docs-mcp__search_ibm_docs` で裏取りする
- **IMPORTANT**: 生成 Jython は Jython 2.x 制約を守る(f-string 禁止 / 日本語は `u"..."` / Windows パスは `/` 区切り / `except E, e:` 形式 / `pathlib`・`open(encoding=)` 禁止)
- **IMPORTANT**: `table` / `dataaudit` ノードに `encoding` プロパティを設定しない(存在しない)。`sample` で `first_n` を効かせるには `sample_type=u"First"` をセットで指定する
- **IMPORTANT**: 出力 CSV/TXT は **UTF-8 BOM 付き** に変換し、AI が読むのは `_utf8_bom.*` 側に限定する
- **NEVER**: `.str` 保存(`taskrunner.saveStreamToFile(stream, path)`)を省略する。clemb はメモリ上のストリームを実行後に破棄するため、保存しないと再現性が失われる
- **IMPORTANT**: `execute_clemb` 呼び出し時は `log_file=<RUN_DIR>/logs/clemb_execution.log` を必ず指定する
- **IMPORTANT**: 成果物は `runs/run_XXX/` 単位で同じ run 配下に集約する。種類別フォルダ横断管理は禁止
- 分類・数値予測では `Target` を 1 つだけ設定、クラスタリングでは Target を設定しない
- モデルノードは `autoclassifier` / `autonumeric` / `autocluster` のいずれかに限定する(個別アルゴリズム単体は対象外)
- エラーは `[SPSS_JYTHON_FAILED] phase=<phase>` 形式で、どの phase で失敗したか分かる形で返す
- 最小限の変更のみ。無関係コードのリファクタや一括書き換えは禁止

## Workflow
- セッション開始時、直前 run の `reports/summary_report.md` があれば最初に読む
- 曖昧依頼でも欠落情報はスキル既定値で進め、確認事項として最終報告に残す(質問で停滞させない)
- フロー: スキル選択 → Jython 生成 → `execute_clemb` 実行 → ログ確認 → フェーズ2 サマリーレポート生成
- clemb 実行成功時のみフェーズ2 を実施。失敗・未実行時は `reports/summary_report.md` を作らず、最終報告にその旨を残す
- 最終報告は **主な出力先 / 置いた仮定 / 確認事項 / 次工程** の 4 ブロックを必ず含める

## Out of scope
- 既存 `.str` / `.py` の修正(`spss-modeler-stream-edit` 系スキルに委譲)
- 既存スクリプトの解説(`spss-modeler-stream-explain` 系スキルに委譲)
- 高度な前処理・特徴量作成・欠損補完・外れ値除外
- ハイパーパラメータの精密チューニング
- .pptx / HTML / PDF へのレポート変換

## 詳細リファレンス
スキル本体の `SKILL.md` および `_shared/` 配下のガイド(テンプレ・タスク種別・モデル評価・出力契約・フェーズ2 レポート手順)を参照する。AGENTS.md には詳細仕様を重複させない。

**対象**: SPSS Modeler 19.0.0 / Jython 2.7
