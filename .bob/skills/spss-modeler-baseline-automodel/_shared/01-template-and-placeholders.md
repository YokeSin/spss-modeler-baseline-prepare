# 01. テンプレート前提とプレースホルダー

`templates/baseline_templates.py` をベースに Jython を生成する際の、テンプレート構成・プレースホルダー・置換ルール・Jython 2.x 注意点をまとめる。

---

## 1. テンプレート前提

Jython 生成では `templates/baseline_templates.py` を土台にする。テンプレートは CSV 入力を前提に、以下を 1 ファイル内で行う。

1. run 配下の標準フォルダ(`streams/` `outputs/` `pmml/` `logs/`)を `ensure_dir` で作成
2. CSV 入力ノード作成
3. Type ノード作成
4. データ監査 HTML 出力
5. 先頭 10 行サンプル HTML 出力
6. 必要に応じて Partition ノード作成
7. AutoModel ノード作成
8. ストリーム保存(モデル前)
9. モデル構築実行
10. 構成モデルごとの PMML XML 出力(`<RUN_DIR>/pmml/` 配下)
11. モデル適用ノード作成
12. 必要に応じて Analysis HTML・Evaluation HTML 出力
13. 出力 HTML を UTF-8 BOM 付きへ変換
14. 評価ノード付きストリーム再保存

`sample` / `dataaudit` / `analysis` / `evaluation` ノードはいずれも `output_format = "HTML"` を指定し、`<RUN_DIR>/outputs/` 配下に `.html` 拡張子で出力する。形式を揃えることでブラウザで一貫して閲覧できる。

`scripts/` フォルダは skill 側で生成 Jython を配置する責務(テンプレート自身は作らない)。run 配下の標準構造とフォルダ役割は [04-output-and-report.md](04-output-and-report.md) §1 を参照。

---

## 2. プレースホルダー一覧

テンプレート内の `<...>` は必ず具体値に置換する。生成後に未置換が残っていないことを確認する。

| プレースホルダー | 内容 | 例 |
|---|---|---|
| `<INPUT_CSV_PATH>` | 入力 CSV の絶対パス | `C:/data/customer.csv` |
| `<RUN_DIR>` | 実行ディレクトリ | `C:/work/runs/run_001` |
| `<STREAM_FILENAME>` | 保存する str 名 | `baseline.str` |
| `<INPUT_NODE_DISPLAY_NAME>` | 入力ノード表示名 | `顧客CSV` |
| `<INPUT_ENCODING>` | 入力文字コード | `SystemDefault`, `UTF-8`, `MS932` |
| `<DELIMITER>` | 区切り文字 | `,`, `\t` |
| `<FIELD_TYPES_ENTRIES>` | Type ノードの型設定 | `u"年齢": u"Range",` |
| `<FIELD_VALUES_ENTRIES>` | Flag/Set の値設定 | `u"性別": [u"F", u"M"],` |
| `<FIELD_DIRECTIONS_ENTRIES>` | role/direction 設定 | `u"解約": u"Target",` |
| `<MODEL_NODE_TYPE>` | AutoModel ノード種別 | `autoclassifier` |
| `<MODEL_NODE_DISPLAY_NAME>` | モデルノード表示名 | `自動分類` |
| `<MODEL_PROPS_ENTRIES>` | モデルプロパティ | `"number_of_models": 5,` |
| `<INCLUDE_PARTITION>` | Partition を作るか | `True` / `False` |
| `<INCLUDE_ANALYSIS>` | Analysis を作るか | `True` / `False` |
| `<INCLUDE_EVALUATION>` | Evaluation を作るか | `True` / `False` |

---

## 3. 入力ノード(variablefile)プロパティ

CSV では原則として以下を設定する。

```python
set_props(variablefile_node, {
    "full_filename": input_csv,
    "read_field_names": True,
    "delimit_other": True,
    "other": u"<DELIMITER>",
    "decimal_symbol": u"Period",
    "encoding": u"<INPUT_ENCODING>"
})
```

Excel・DB・固定長などの非 CSV 形式は、本テンプレートの対象外。IBM Docs(`mcp__ibm-docs-mcp__search_ibm_docs` / `get_ibm_topic`)で正式なノードタイプとプロパティを確認してから別構成で生成する。

---

## 4. 置換時の注意

- Jython 2.x 前提のため、日本語文字列は原則 `u"..."` にする。
- Windows パスは `/` 区切りに寄せると安全。例: `C:/data/input.csv`。`\` を使う場合はエスケープ崩れに注意する。
- 辞書エントリの末尾カンマは許容される。
- 空にする場合は、コメントだけ残して空辞書にする。

```python
field_types = {
    # 明示設定なし。Modeler の自動推定に委ねる。
}
```

---

## 5. SPSS Modeler / Jython 2.x 注意点

- SPSS Modeler スクリプトは Jython 2.x 前提。
- f-string、型ヒント、Python 3 専用構文は使わない。
- 例外構文は `except Exception, e:` 形式を維持する。
- `print()` 関数形式ではなく `print u"..."` 形式を使う。
- 日本語文字列は `u"..."` を使う。
- Java クラスを利用するファイル操作部分(`File`, `FileInputStream`, `Charset` など)はテンプレートの形を維持する。
- `stream = modeler.script.stream()` は冒頭で 1 回だけ取得する。
- `stream.setPropertyValue("encoding", u"UTF-8")` を設定する。
- `model_node.run(model_results)` の結果が空の場合はエラーにする。
- 複合モデルの個別モデル取得(`getIndividualModelResults`)は失敗することがあるため、失敗時は警告に留める。
- 個別 PMML XML 出力に失敗するモデルがあっても、他のモデル出力は継続する(try/except でスキップ)。
- `filter_individual_model_output` は環境により失敗する可能性があるため、try/except で警告扱いにする。
- 出力ファイルは存在確認と 0 バイト確認(`require_created_file`)を行う。
- 成功時は一時 raw ファイルを削除してよい。失敗時は調査用に残す。
- エラー時は `[SPSS_JYTHON_FAILED] phase=<phase>` 形式で再 raise する。
