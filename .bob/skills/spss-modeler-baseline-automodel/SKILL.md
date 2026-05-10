---
name: spss-modeler-baseline-automodel
description: CSV 等の入力データと分析目的から、SPSS Modeler でベースライン自動モデルストリーム(.str)を新規作成する。ユーザーが「ベースラインを作って」「予測モデル作って」「AutoModel で分類/数値予測/クラスタリングして」「とりあえずモデル組んで」「.str を作って」のいずれかに該当する依頼をしたとき、または分析目的が示されモデル構築が必要なときに使う。担当範囲は入力ノード・Typeノード・サンプル・データ監査・AutoModel(autoclassifier/autonumeric/autocluster)・PMML XML 出力・Analysis/Evaluation・.str 保存。clemb 実行成功後にはフェーズ2として Markdown サマリーレポートを生成する(詳細は phase2-summary-report.md)。既存スクリプトの編集は spss-modeler-stream-edit、解説のみは spss-modeler-stream-explain に委譲する。
---

# SPSS Modeler Baseline AutoModel Skill

## 目的

ユーザーが提示した入力データと分析目的をもとに、SPSS Modelerでベースラインの自動モデルストリームを作成し、モデル構築・評価・PMML出力までを 1 本の `.str` で完結させる。

このSkillは `templates/baseline_templates.py` をテンプレートとして使い、タスク種別(分類/数値予測/クラスタリング)に応じた AutoModel ノードと評価ブランチを生成する。

## 完了条件

以下が生成・確認できたら完了とする。

- `<RUN_DIR>` 配下に標準フォルダ(`scripts/` `streams/` `outputs/` `pmml/` `logs/`)が揃っている
- 生成 Jython が `<RUN_DIR>/scripts/<basename>.py` に配置されている
- 入力データに対応した入力ノードが作成されている
- Typeノードが入力ノードの後ろに接続されている
- 先頭10行のサンプルHTMLが `<RUN_DIR>/outputs/` に出力されている
- データ監査HTMLが `<RUN_DIR>/outputs/` に出力されている
- AutoModelノードによりモデル構築が完了している
- 構成モデルごとの PMML XML が `<RUN_DIR>/pmml/` 配下に出力されている
- (分類・数値予測の場合) Analysis HTML が出力されている
- (分類の場合) Evaluation HTML が出力されている
- 評価ノード付きの保存済みストリーム `.str` が `<RUN_DIR>/streams/` に作成されている
- 実行した場合、clemb 実行ログが `<RUN_DIR>/logs/clemb_execution.log` に残っている
- clemb 実行が成功した場合、Markdown サマリーレポートが `<RUN_DIR>/reports/summary_report.md` に生成されている(UTF-8 BOM なし。詳細は [phase2-summary-report.md](phase2-summary-report.md))
- 報告に出力パス・前提・置いた仮定・確認事項が含まれている

## 対象範囲

- CSV 入力ノードの作成(Excel/DB/固定長も対象範囲内だがテンプレ非対応のため、`mcp__ibm-docs-mcp__search_ibm_docs` でノード仕様を裏取りした上で最小構成で生成し、確認事項として残す)
- Typeノードによる型・values・direction の設定
- 先頭 10 行サンプル HTML 出力
- データ監査 HTML 出力
- 必要に応じた Partition ノード
- AutoModel ノード(`autoclassifier` / `autonumeric` / `autocluster`)の作成・実行
- 構成モデルごとの PMML XML 出力
- Model Applier ノード作成
- Analysis ノード HTML 出力(分類・数値予測)
- Evaluation ノード HTML 出力(分類)
- 出力 HTML の UTF-8 BOM 変換
- 評価ノード付き `.str` の保存
- clemb 実行成功後の Markdown サマリーレポート生成(フェーズ2 / 詳細は [phase2-summary-report.md](phase2-summary-report.md))

## 対象外

- 既存スクリプトの修正は `spss-modeler-stream-edit` に委ねる
- 既存スクリプトの解説は `spss-modeler-stream-explain` に委ねる
- 高度な前処理、特徴量作成、欠損補完、外れ値除外
- カスタムモデル(個別アルゴリズム単体)の構築
- ハイパーパラメータの精密チューニング
- プレゼン資料(.pptx 等)の作成、サマリーレポートの PDF 変換(必要な場合は Markdown レンダラーの印刷機能で代替する)

## 最初に確認すること

ユーザーの初回プロンプトから以下を抽出する。

1. **入力データ形式**(CSV / Excel / DB / 固定長 / その他)。**不在時:質問する**(ファイル拡張子から推定できる場合は推定+確認事項)
2. **入力データの場所**(ファイルパス / フォルダ / DB 接続情報)。**不在時:質問する**
3. **分析目的と想定意思決定**(例: 解約予測 → 解約阻止キャンペーン対象選定 / 売上予測 → 月次予算配分 / 顧客セグメント → DM 配信戦略 / まず中身を見たい)。意思決定を聞き出す目的は、フェーズ2 のサマリーレポート「ビジネスへの示唆」で「予測精度がその意思決定に耐えるか」を評価するため。**不在時:仮置きで進める**(レポートで精度水準のみ評価する旨を伝える)
4. **タスク種別**(分類 / 数値予測 / クラスタリング)。判断基準は [_shared/02-task-and-type.md](_shared/02-task-and-type.md) の §1。**不在時:仮置きで進める**(ターゲット候補・データ性質から推定し、確認事項に残す)
5. **ターゲット変数**(分類・数値予測の場合のみ)。**不在時:仮置きで進める**(候補が複数 / 0 件のときは質問する)
6. **出力先**(未指定なら `runs/run_XXX/` 配下を作成)。**不在時:既定値で進める**(`runs/run_XXX/` 連番)
7. **文字コード・区切り文字・ヘッダ有無**。**不在時:既定値で進める**(`SystemDefault` / カンマ / ヘッダあり、確認事項に残す)

## 不足情報がある場合の扱い

以下が不明な場合は質問する。

- 入力データのパスが不明
- データ形式が不明
- DB 接続情報が不足している
- 分類・数値予測なのにターゲット候補が見つけられない
- 出力先が厳密に必要なのに未指定

CSV ファイルパスとタスク種別・ターゲットが明確な場合は、追加質問を最小化し、既定値で進める。

## 既定値

ユーザー指定がない場合は、以下を既定値とする。

- サンプル件数: 10 行
- CSV 区切り文字: カンマ
- CSV ヘッダ: あり
- 小数点記号: `Period`
- 入力エンコーディング: `SystemDefault`
- ストリームエンコーディング: UTF-8
- 最終出力 HTML(sample / dataaudit / analysis / evaluation): UTF-8 BOM 付き
- 候補モデル数(`number_of_models`): 5
- Partition: 学習 70% / テスト 30%、`random_seed=12345`
- run フォルダ名: `runs/run_XXX/`(連番)

詳細な既定値は [_shared/03-model-and-evaluation.md](_shared/03-model-and-evaluation.md) を参照する。

## 基本フロー

### ストリーム構成

```text
input_node
  └─ type_node
       ├─ sample_node → table_node → sample_html
       ├─ dataaudit_node → audit_html
       └─ (partition_node →) model_node
              ├─ → 構成モデル毎の PMML XML
              └─ → model_applier_node
                     ├─ analysis_node → analysis_html   (分類/数値予測)
                     └─ evaluation_node → evaluation_html (分類)
```

クラスタリングの場合は Partition / Analysis / Evaluation を作らず、AutoCluster ノードまでで完結する。

### run フォルダ構造

```text
runs/run_XXX/
├── scripts/   # 生成 Jython 本体 (skill が配置)
├── streams/   # .str (テンプレート出力)
├── outputs/   # サンプル HTML / データ監査 HTML / Analysis HTML / Evaluation HTML
├── pmml/      # 構成モデル毎の PMML XML
├── logs/      # clemb_execution.log
└── reports/   # サマリーレポート Markdown (フェーズ2 / skill が clemb 成功後に作成)
```

詳細は [_shared/04-output-and-report.md](_shared/04-output-and-report.md) §1 を参照。

## 作業手順

### 0. 入力データと既存 run を読む

作業前に以下を実施し、後続ステップを実データ起点にする(ジェネリックな推測でテンプレを埋めない)。

1. **入力データを読む**: 入力が CSV ならファイルのヘッダ行と先頭 5〜10 行を Read し、列名・推定型・候補ターゲット・既存 `Partition` 列の有無を把握する。CSV 以外(Excel/DB/固定長)なら `mcp__ibm-docs-mcp__search_ibm_docs` で対応する入力ノード仕様を先に引く。
2. **既存 run を確認する**: `runs/` を Glob し、既存 `run_XXX` フォルダ番号から次の連番を決める(例: `run_003` まであれば `run_004`)。ユーザーが run フォルダを明示している場合はそれに従う。
3. **Partition 列の有無を判断材料にする**: 入力データに既に `Partition` 列があれば、新規 Partition ノードを追加しない選択肢を持つ(最終決定は §5)。

ここで得た情報は §4(Type 設定)・§5(モデル/評価ブランチ)・§9(報告)で参照する。

### 1. 入力形式とタスク種別を判断する

CSV の場合は `templates/baseline_templates.py` をベースにする。
CSV 以外の場合は、IBM Docs(`mcp__ibm-docs-mcp__search_ibm_docs` / `get_ibm_topic`)で正式な入力ノードとプロパティを裏取りしてから別構成で生成する。

タスク種別の判断基準は [_shared/02-task-and-type.md](_shared/02-task-and-type.md) §1 を参照。

### 2. パスを決める

以下を確定する。未指定は run フォルダ配下に作成する。

- 入力データパス
- `<RUN_DIR>`(`runs/run_XXX/`)
- 生成 Jython の配置先(`<RUN_DIR>/scripts/<basename>.py`)
- ストリームファイル名(`baseline.str` 等、`<RUN_DIR>/streams/` 配下)
- clemb 実行ログのパス(`<RUN_DIR>/logs/clemb_execution.log`)

出力先の標準構造とフォルダ役割は [_shared/04-output-and-report.md](_shared/04-output-and-report.md) §1 を参照。

### 3. テンプレートのプレースホルダーを置換する

`templates/baseline_templates.py` の `<...>` 形式プレースホルダーを全て置換する。
プレースホルダー一覧と置換時の注意は [_shared/01-template-and-placeholders.md](_shared/01-template-and-placeholders.md) §2〜§4 を参照。

### 4. Type 設定を決める

`field_types` / `field_values` / `field_directions` を、データ性質と分析目的から決める。
分類・数値予測ではターゲットを 1 つだけ `Target` に設定する。クラスタリングでは Target を設定しない。
詳細は [_shared/02-task-and-type.md](_shared/02-task-and-type.md) §2 を参照。

### 5. モデルノードと評価ブランチの設定を決める

`<MODEL_NODE_TYPE>` / `<MODEL_PROPS_ENTRIES>` / `<INCLUDE_PARTITION>` / `<INCLUDE_ANALYSIS>` / `<INCLUDE_EVALUATION>` を、タスク種別に応じて決める。
ON/OFF の対応表とプロパティ既定値は [_shared/03-model-and-evaluation.md](_shared/03-model-and-evaluation.md) を参照。

### 6. Jython を生成し、ユーザーに提示する

生成 Jython は `<RUN_DIR>/scripts/<basename>.py` に配置する(`scripts/` フォルダがなければ作る)。
生成後チェックリスト([_shared/04-output-and-report.md](_shared/04-output-and-report.md) §3)を全て満たしていることを確認してから提示する。

### 7. 必要に応じて実行する

ユーザーから明示的に実行を求められた場合のみ、`mcp__spss-clemb-mcp__execute_clemb` で実行する。引数は以下:

- `script_file`: `<RUN_DIR>/scripts/<basename>.py`
- `log_file`: `<RUN_DIR>/logs/clemb_execution.log`(必ず指定。省略するとログが残らない)

実行後、出力ファイルが存在し空でないこと、および `logs/clemb_execution.log` にエラー文字列(`[SPSS_JYTHON_FAILED]` など)がないことを確認する。

### 8. サマリーレポートを生成する(フェーズ2)

clemb 実行に成功した場合のみ実行する。詳細手順は [phase2-summary-report.md](phase2-summary-report.md) を参照。

概要:

- `<RUN_DIR>/logs/clemb_execution.log` にエラー(`[SPSS_JYTHON_FAILED]` 等)が無いことを確認する
- `<RUN_DIR>/outputs/`, `<RUN_DIR>/pmml/`, `<RUN_DIR>/scripts/`, `<RUN_DIR>/streams/` の中身を読み、ユーザーから得た分析目的・前提と統合する
- `<RUN_DIR>/reports/summary_report.md` を Markdown(UTF-8 BOM なし)で生成する。構成は次の 6 章: 1) 分析の目的と前提 / 2) 分析結果の概要(キーバリュー表 + `outputs/` 配下への相対リンク集) / 3) 分析結果から読み取れること(データ特徴・モデル比較・誤分類傾向・評価グラフ所見) / 4) ビジネスへの示唆(3 段落) / 5) 次に取るべきアクション(3〜5 個) / 6) 確認ポイント(severity 付き 4〜6 個)
- 数値・表は AI が `outputs/` 配下の HTML を Read で読み、Markdown 表に直書きする。詳細は元 HTML への相対リンクで誘導し、Markdown 側に重複データを大量に書かない。プレースホルダー方式は使わない
- ユーザーが「レポート不要」と明示したときはスキップする

実行していない、または clemb 実行が失敗している場合は本ステップをスキップし、その旨を最終報告に残す。

### 9. 結果を報告する

最終報告には最低限以下の 4 ブロックを含める(詳細フォーマット例は [_shared/04-output-and-report.md](_shared/04-output-and-report.md) §2 を参照)。

- **主な出力先**: 実際に作成した `scripts/` `streams/` `outputs/` `pmml/` `logs/` `reports/` 配下のファイルを絶対パスで列挙する。サマリーレポート (`<RUN_DIR>/reports/summary_report.md`) を生成した場合は必ずパスを含め、Markdown プレビューで開く想定であることを 1 行添える。
- **置いた仮定**: 文字コード・区切り文字・Partition の扱い・ターゲット推定の根拠など、ユーザー指定が無く skill 側で決めた項目を列挙する。
- **確認事項**: 後追いでユーザーに確認したい点(型推定の妥当性、ターゲット選定、モデルプロパティの精度など)。
- **次工程**: フェーズ2 サマリーレポートを生成済みか、未生成か(未生成の場合は理由: clemb 未実行 / 実行失敗 / ユーザーが不要と明示)。

次工程への引き継ぎ情報は [_shared/04-output-and-report.md](_shared/04-output-and-report.md) §4 を参照。

## 重要ルール

- モデルノードは `autoclassifier` / `autonumeric` / `autocluster` のいずれかに限定する
- 分類・数値予測では `Target` を必ず 1 つだけにする
- クラスタリングでは `Target` を設定しない
- 入力ノードの種類とプロパティが不確かな場合は IBM Docs で確認する
- モデルプロパティ名・値が不確かな場合は断定せず、最小設定+確認事項で残す
- 最終出力 HTML は UTF-8 BOM 付きに変換する
- 成功時は一時 raw ファイル(`_tmp_*`)を削除する
- 失敗時は調査用に一時 raw ファイルを残す
- エラーは `[SPSS_JYTHON_FAILED] phase=<phase>` 形式で、どの phase で失敗したか分かる形式で返す
- 個別 PMML XML 出力に失敗するモデルがあっても、他のモデル出力は継続する(警告に留める)
- 生成 Jython は必ず `<RUN_DIR>/scripts/` 配下に配置する(run フォルダ直下に置かない)
- `execute_clemb` を呼ぶ際は `log_file` 引数で `<RUN_DIR>/logs/clemb_execution.log` を必ず指定する
- サマリーレポートは clemb 実行成功時のみ生成する。失敗時・未実行時は `<RUN_DIR>/reports/summary_report.md` を作らず、その旨を最終報告に残す

## 詳細リファレンス

### フェーズ2(レポート生成)

| ファイル | 内容 |
|---|---|
| [phase2-summary-report.md](phase2-summary-report.md) | clemb 実行成功後の Markdown サマリーレポート生成フロー・抽出ルール・チェックリスト |
| [templates/section_examples.md](templates/section_examples.md) | 章毎の Markdown スニペット例 (キーバリュー表・モデル比較表・ビジネス示唆 3 段落・確認ポイント等)。AI がコピペ起点に使う |

### _shared/(フェーズ1 詳細)

| ファイル | 内容 |
|---|---|
| [_shared/01-template-and-placeholders.md](_shared/01-template-and-placeholders.md) | テンプレート構成・プレースホルダー一覧・置換ルール・Jython 2.x 注意点 |
| [_shared/02-task-and-type.md](_shared/02-task-and-type.md) | タスク種別判断・Type ノード設定・よくあるユーザー指定への対応 |
| [_shared/03-model-and-evaluation.md](_shared/03-model-and-evaluation.md) | AutoModel プロパティ・Partition/Analysis/Evaluation ノード設定 |
| [_shared/04-output-and-report.md](_shared/04-output-and-report.md) | 出力ファイル契約・報告形式・生成後チェックリスト・次Skill引き継ぎ |
