# 04. 出力ファイル契約・報告形式・チェックリスト

生成 Jython の出力先、報告フォーマット、ユーザーへ渡す前の確認項目をまとめる。

---

## 1. 出力ファイル契約

`<RUN_DIR>` 配下を以下の標準構造にする。

```text
<RUN_DIR>/
  scripts/
    baseline.py                  # 生成した Jython 本体 (skill が配置)
  streams/
    baseline.str                 # 保存される .str
  outputs/
    sample_baseline.html
    dataaudit_baseline.html
    analysis_baseline.html       # Analysis 有効時のみ
    evaluation_baseline.html     # Evaluation 有効時のみ
  pmml/
    01_xxx.xml                   # 構成モデルごとの PMML XML
    02_xxx.xml
    ...
  logs/
    clemb_execution.log          # clemb 実行ログ (execute_clemb の log_file)
  reports/
    summary_report.md            # フェーズ2サマリーレポート Markdown (clemb 実行成功時のみ、UTF-8 BOM なし)
```

### 1.1 フォルダ役割と作成主体

| フォルダ | 内容 | 作成主体 |
|---|---|---|
| `scripts/` | 生成した Jython 本体 | skill(clemb 起動前に配置) |
| `streams/` | 保存される `.str` | テンプレート(Jython 内 `ensure_dir`) |
| `outputs/` | HTML 形式の実行成果物(sample / dataaudit / analysis / evaluation) | テンプレート |
| `pmml/` | 構成モデルごとの PMML XML | テンプレート |
| `logs/` | clemb 実行ログ | テンプレート + skill が `execute_clemb` の `log_file` で指定 |
| `reports/` | サマリーレポート Markdown(フェーズ2) | skill(clemb 実行成功後、`outputs/` 配下の HTML を Read で読み、`<RUN_DIR>/reports/summary_report.md` を Markdown で直書き生成。詳細は [phase2-summary-report.md](../phase2-summary-report.md)) |

### 1.2 必須出力(全タスク共通)

- `.str` ファイル
- 先頭 10 行サンプル HTML
- データ監査 HTML
- PMML XML 格納フォルダ(個別モデルが 0 件のときも空フォルダで作成する)
- clemb 実行ログ(実行した場合)
- サマリーレポート Markdown(clemb 実行成功時のみ。`<RUN_DIR>/reports/summary_report.md`)

### 1.3 タスク別出力

| タスク | analysis HTML | evaluation HTML | PMML XML |
|---|---:|---:|---:|
| 分類 | 出力 | 出力 | 出力 |
| 数値予測 | 出力 | 原則なし | 出力 |
| クラスタリング | 原則なし | 原則なし | 出力 |

### 1.4 文字コード

- Modeler からの raw 出力は一時 HTML(`_tmp_*.html`、`outputs/` 配下)に出す。
- 最終 HTML(sample / dataaudit / analysis / evaluation)はすべて UTF-8 BOM 付きへ変換する(`convert_to_utf8_bom`)。ブラウザは BOM を `meta charset` 宣言より優先するため、ソース HTML 内の charset 宣言が異なっていても表示は崩れない。
- 成功時は一時ファイルを削除してよい。
- 失敗時は調査用に一時ファイルが残る可能性がある。

### 1.5 clemb 実行(`mcp__spss-clemb-mcp__execute_clemb`)の引数

ユーザーから明示的に実行を求められた場合、以下の引数で呼び出す。

```text
script_file = <RUN_DIR>/scripts/<basename>.py
log_file    = <RUN_DIR>/logs/clemb_execution.log
```

`log_file` は省略するとログが残らないため、必ず指定する。`working_directory` は通常指定不要(`script_file` を絶対パスで渡す前提)。

---

## 2. 生成後の報告形式

Jython 生成・実行後、ユーザーに以下を報告する。

```text
生成ファイル:
- Jython 本体: <RUN_DIR>/scripts/<basename>.py

前提:
- 入力 CSV: <path>
- タスク種別: <分類/数値予測/クラスタリング>
- AutoModel ノード: <autoclassifier/autonumeric/autocluster>
- ターゲット: <target or なし>
- 想定意思決定: <text or 未確認>
- 文字コード: <encoding>
- 区切り文字: <delimiter>

主な出力先:
- ストリーム: <RUN_DIR>/streams/<STREAM_FILENAME>
- サンプル HTML: <RUN_DIR>/outputs/sample_baseline.html
- データ監査 HTML: <RUN_DIR>/outputs/dataaudit_baseline.html
- PMML XML: <RUN_DIR>/pmml/
- 分析 HTML: <path or なし>
- 評価 HTML: <path or なし>
- 実行ログ: <RUN_DIR>/logs/clemb_execution.log
- サマリーレポート: <RUN_DIR>/reports/summary_report.md (clemb 実行成功時のみ)

置いた仮定:
- <仮定 1>
- <仮定 2>

実行前の確認事項:
- <確認事項 1>
- <確認事項 2>
```

---

## 3. 生成後チェックリスト

Jython をユーザーに渡す前に、以下を確認する。

- [ ] `<...>` 形式の未置換プレースホルダーが残っていない
- [ ] 入力 CSV パスが設定されている
- [ ] run フォルダ(`<RUN_DIR>`)が設定されている
- [ ] `.str` ファイル名が設定されている
- [ ] Jython の配置先が `<RUN_DIR>/scripts/` 配下になっている
- [ ] `field_types` が Jython 2.x で有効な辞書になっている
- [ ] `field_values` が Jython 2.x で有効な辞書になっている
- [ ] `field_directions` が Jython 2.x で有効な辞書になっている
- [ ] 分類・数値予測では `Target` が 1 つだけ
- [ ] クラスタリングでは `Target` がない
- [ ] `<MODEL_NODE_TYPE>` が `autoclassifier` / `autonumeric` / `autocluster` のいずれか
- [ ] `<INCLUDE_PARTITION>` / `<INCLUDE_ANALYSIS>` / `<INCLUDE_EVALUATION>` が `True` または `False`
- [ ] `MODEL_PROPS_ENTRIES` のキー名に不確かな断定がない
- [ ] パス文字列が壊れていない
- [ ] PMML XML 出力フォルダが `<RUN_DIR>/pmml/` になっている
- [ ] 実行時は `execute_clemb` の `log_file` を `<RUN_DIR>/logs/clemb_execution.log` に指定する
- [ ] エラー時に `phase` が出る構造を維持している

---

## 4. 次 Skill への引き継ぎ情報

別の次工程(プレゼン資料化、HTML/PDF 化、別 run の比較など)に渡す情報は以下。
本 skill のフェーズ2(サマリーレポート Markdown 生成)はこのスキル内で完結する点に注意する。

- サマリーレポートパス(`<RUN_DIR>/reports/summary_report.md` / 生成済みの場合)
- 分析目的・想定意思決定・タスク種別(分類/数値予測/クラスタリング)
- 入力データパス
- 生成 Jython パス(`<RUN_DIR>/scripts/<basename>.py`)
- 保存済み `.str` パス(`<RUN_DIR>/streams/<STREAM_FILENAME>`)
- サンプル HTML / データ監査 HTML / Analysis HTML / Evaluation HTML パス
- PMML XML フォルダパス(`<RUN_DIR>/pmml/`)と出力された個別モデル一覧
- 実行ログパス(`<RUN_DIR>/logs/clemb_execution.log`)
- 採用ターゲット変数とその根拠
- このSkillで置いた仮定
- ユーザーに確認が必要な点(型・ターゲット・モデルプロパティ等)
