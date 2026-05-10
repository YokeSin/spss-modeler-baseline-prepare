# 02. タスク種別判断と Type ノード設定

ユーザーの分析目的とデータの性質から、タスク種別(分類/数値予測/クラスタリング)を決め、Type ノードの `type` / `values` / `direction` を設定する。

---

## 1. タスク種別判断

### 1.1 分類: autoclassifier

以下のような目的なら分類と判断する。

- 解約する/しない
- 購入する/しない
- 不正/正常
- 優良/一般/離反予備軍
- ランク・区分・カテゴリの予測

設定方針:

```text
<MODEL_NODE_TYPE>         = autoclassifier
<MODEL_NODE_DISPLAY_NAME> = 自動分類
<INCLUDE_PARTITION>       = True
<INCLUDE_ANALYSIS>        = True
<INCLUDE_EVALUATION>      = True
```

ターゲットは `Flag` または `Set` が基本。代表的な評価指標は `Accuracy`。

### 1.2 数値予測: autonumeric

以下のような目的なら数値予測と判断する。

- 売上予測
- 需要予測
- 金額予測
- 数量予測
- スコア・日数・単価などの連続値予測

設定方針:

```text
<MODEL_NODE_TYPE>         = autonumeric
<MODEL_NODE_DISPLAY_NAME> = 自動数値
<INCLUDE_PARTITION>       = True
<INCLUDE_ANALYSIS>        = True
<INCLUDE_EVALUATION>      = False
```

ターゲットは `Range` が基本。代表的な評価指標は `Correlation` または `RMSE`。

### 1.3 クラスタリング: autocluster

以下のような目的ならクラスタリングと判断する。

- 顧客セグメントを作りたい
- 類似グループに分けたい
- 教師なしで傾向を見たい
- ターゲットなしで分類したい

設定方針:

```text
<MODEL_NODE_TYPE>         = autocluster
<MODEL_NODE_DISPLAY_NAME> = 自動クラスタリング
<INCLUDE_PARTITION>       = False
<INCLUDE_ANALYSIS>        = False
<INCLUDE_EVALUATION>      = False
```

クラスタリングでは `Target` を設定しない。利用する項目は原則 `Input`。

---

## 2. Type ノード設定

### 2.1 type の基本

| データの性質 | Modeler type | 例 |
|---|---|---|
| 連続値 | `Range` | 年齢、売上、数量、金額 |
| 2 値 | `Flag` | 解約有無、購入有無、性別が 2 値の場合 |
| カテゴリ | `Set` | 地域、業種、商品カテゴリ |
| 順序付きカテゴリ | `OrderedSet` | ランク、満足度段階 |
| 日付/時刻 | `Date`, `Time`, `Timestamp` | 申込日、購入日時 |
| 自由記述 | 原則除外候補 | コメント、問い合わせ本文 |

### 2.2 direction の基本

| 役割 | direction | 方針 |
|---|---|---|
| 目的変数 | `Target` | 分類・数値予測で 1 つだけ設定 |
| 説明変数 | `Input` | モデルに使う候補 |
| 使わない項目 | `None` | ID、氏名、住所、自由記述など |

注意:

- 分類・数値予測では `Target` は必ず 1 つにする。
- クラスタリングでは `Target` を使わない。
- ID、会員番号、伝票番号などのキー項目は通常 `None`。
- 顧客名、住所、電話番号、メールアドレスなど個人識別に近い項目は通常 `None`。
- 型や使い方が曖昧な項目は無理に断定せず確認事項に残す。

### 2.3 field_types 例

```python
field_types = {
    u"年齢": u"Range",
    u"性別": u"Flag",
    u"地域": u"Set",
    u"購入金額": u"Range",
    u"解約有無": u"Flag",
}
```

### 2.4 field_values 例

```python
field_values = {
    u"性別": [u"F", u"M"],
    u"解約有無": [u"0", u"1"],
}
```

`values` は明確な候補値が分かる場合だけ設定する。候補値が不明な Set 項目では、無理に入れない。

### 2.5 field_directions 例: 分類

```python
field_directions = {
    u"顧客ID": u"None",
    u"年齢": u"Input",
    u"性別": u"Input",
    u"地域": u"Input",
    u"購入金額": u"Input",
    u"解約有無": u"Target",
}
```

### 2.6 field_directions 例: クラスタリング

```python
field_directions = {
    u"顧客ID": u"None",
    u"年齢": u"Input",
    u"性別": u"Input",
    u"地域": u"Input",
    u"購入金額": u"Input",
}
```

---

## 3. よくあるユーザー指定への対応

### 3.1 「解約予測をしたい」

- タスク: 分類
- ノード: `autoclassifier`
- ターゲット候補: `解約`, `解約有無`, `churn`, `退会フラグ`
- 評価: Analysis + Gains チャート

### 3.2 「売上を予測したい」

- タスク: 数値予測
- ノード: `autonumeric`
- ターゲット候補: `売上`, `売上金額`, `sales`, `amount`
- 評価: Analysis のみ

### 3.3 「顧客を分類したい」

文脈に注意する。

- ターゲット項目があり、カテゴリを予測したい → 分類
- ターゲットなしで似た顧客を分けたい → クラスタリング

曖昧な場合は、以下のように確認する。

```text
「顧客を分類」は、正解ラベルを予測する分類モデルでしょうか。
それとも、正解ラベルなしで似た顧客をグループ化するクラスタリングでしょうか。
```

ただし、プロンプト内に「ターゲットなし」「セグメント」「似た傾向」などがあればクラスタリング寄りで判断する。

### 3.4 「まずベースラインでよい」

- 高度な前処理は入れない。
- 入力、Type、AutoModel、評価、PMML 出力までに留める。
- 欠損補完、外れ値除外、特徴量作成は確認事項または次工程に回す。
