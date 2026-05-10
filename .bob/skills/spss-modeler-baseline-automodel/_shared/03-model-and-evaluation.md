# 03. モデルプロパティと評価ノード設定

AutoModel ノード(`autoclassifier` / `autonumeric` / `autocluster`)のプロパティと、Partition / Analysis / Evaluation ノードの ON/OFF・既定値をまとめる。

---

## 1. モデルプロパティ設定

`<MODEL_PROPS_ENTRIES>` は、モデルノードの `set_props(model_node, {...})` に入る辞書エントリとして生成する。

### 1.1 共通方針

- 指定がなければ候補モデル数は 5 にする。
- ユーザーが評価指標を指定した場合は、それを優先する。
- プロパティ名や値が不確かな場合は断定せず、最小設定に留める。
- IBM SPSS Modeler のバージョン差で動かない可能性があるプロパティは、確認事項に残す。

### 1.2 分類モデル(autoclassifier)

```python
"ranking_measure": u"Accuracy",
"number_of_models": 5,
```

候補になる評価指標:

- `Accuracy`
- `AUC`
- `Profit`
- `Lift`

実際に利用できる値は Modeler バージョンに依存する可能性がある。

### 1.3 数値予測モデル(autonumeric)

```python
"ranking_measure": u"Correlation",
"number_of_models": 5,
```

候補になる評価指標:

- `Correlation`
- `RMSE`
- `MAE`

バージョンやノード設定により、指定名が異なる可能性があるため注意する。

### 1.4 クラスタリングモデル(autocluster)

```python
"number_of_models": 5,
```

クラスタリングでは、分類・数値予測と同じ精度評価指標を置かない。必要最小限のプロパティにする。

---

## 2. 評価系ノードの ON/OFF

タスク種別に応じて、Partition / Analysis / Evaluation の作成可否を決める。

| タスク | Partition | Analysis | Evaluation |
|---|---:|---:|---:|
| 分類 | True | True | True |
| 数値予測 | True | True | False |
| クラスタリング | False | False | False |

### 2.1 Partition ノード(分類・数値予測)

学習 70%、テスト 30% を標準とする。

```python
set_props(partition_node, {
    "create_validation": False,
    "training_size": 70,
    "testing_size": 30,
    "set_random_seed": True,
    "random_seed": 12345
})
```

### 2.2 Analysis ノード(分類・数値予測)

モデル適用結果に対して Analysis ノードを作る。出力は HTML(他成果物と形式を揃える)。

```python
set_props(analysis_node, {
    "coincidence": True,
    "performance": True,
    "confidence": True,
    "output_mode": "File",
    "output_format": "HTML",
    "full_filename": tmp_analysis_html
})
```

### 2.3 Evaluation ノード(分類)

Gains チャートを HTML 出力する(他成果物と形式を揃える)。数値予測・クラスタリングでは標準では作らない。

```python
set_props(evaluation_node, {
    "chart_type": "Gains",
    "inc_baseline": True,
    "inc_best_line": True,
    "output_mode": "File",
    "output_format": "HTML",
    "full_filename": tmp_evaluation_html
})
```

---

## 3. データ監査(dataaudit)ノード既定値

タスク種別に依らず共通。`display_graphs=True` を指定し、各変数の分布サムネイルグラフを HTML 出力に含める。

```python
set_props(dataaudit_node, {
    "custom_fields": False,
    "display_graphs": True,
    "basic_stats": True,
    "advanced_stats": True,
    "median_stats": True,
    "outlier_detection_method": "std",
    "outlier_detection_std_outlier": 2.0,
    "outlier_detection_std_extreme": 3.0,
    "output_mode": "File",
    "output_format": "HTML",
    "full_filename": tmp_dataaudit_html
})
dataaudit_node.setPropertyValue("calculate", ["Count", "Breakdown"])
```

---

## 4. サンプル(sample)ノード既定値

先頭 10 行を抽出する。

```python
set_props(sample_node, {
    "method": u"Simple",
    "mode": u"Include",
    "sample_type": u"First",
    "first_n": 10
})
```
