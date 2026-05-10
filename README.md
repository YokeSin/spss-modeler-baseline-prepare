# spss-modeler-baseline-prepare

SPSS Modeler でベースライン自動モデル(`.str`)を作るための、IBM Bob 用スキルとエージェント定義をまとめたリポジトリ。

CSV 等の入力データを与えると、IBM Bob が Jython スクリプトを生成・実行し、データ確認 → AutoModel(分類 / 数値予測 / クラスタリング)→ PMML 出力 → 評価 → ストリーム保存までを 1 本のフローで完結させる。

## 動作環境

- Windows
- Python 3.10 以上
- SPSS Modeler 19.0(`clemb` 同梱版)
- Jython 2.7(SPSS Modeler に内包)
- IBM Bob

## 依存 MCP サーバ

本リポジトリ単体では動作せず、以下 2 つの MCP サーバを別途セットアップする必要がある。セットアップ手順は各リポジトリのページを参照。

| 名前 | 用途 | 入手先 |
|---|---|---|
| `spss-clemb-mcp` | SPSS Modeler の `clemb` 経由で Jython を実行 | <https://github.com/hkwd/spss-clemb-mcp> |
| `ibm-docs-mcp` | SPSS Modeler ノード仕様の裏取り | <https://qiita.com/spssfun2017/items/e6142dfa2692a89bec0d> |

## セットアップ

1. 本リポジトリを clone する
2. 上記 2 つの MCP サーバを、各リポジトリのページに記載された手順でセットアップする
3. [.bob/mcp.json](.bob/mcp.json) を開き、2 箇所の `<path-to-...>` を実際の MCP サーバ配置パスに書き換える
   - 例: `"cwd": "C:/Users/your-name/.mcp-servers/spss-clemb-mcp"`
4. IBM Bob を本リポジトリのルートで起動する

## 使い方

`inputs/` に分析対象データ(CSV 等)を配置し、IBM Bob に対して例えば次のように依頼する。

- 「ベースラインを作って」
- 「○○ を予測するモデルを作って」
- 「とりあえず `.str` を組んで」

成果物は `runs/run_XXX/` 配下に集約され、以下が生成される。

- `streams/` — 保存された `.str`
- `outputs/` — サンプル / データ監査 / 評価 HTML
- `pmml/` — 個別モデルの PMML XML
- `scripts/` — 実行された Jython
- `logs/` — clemb 実行ログ
- `reports/` — フェーズ 2 のサマリーレポート(Markdown)

## ディレクトリ構成

```
.
├── .bob/
│   ├── mcp.json                                  # MCP 接続定義
│   └── skills/
│       └── spss-modeler-baseline-automodel/      # 主スキル本体
├── inputs/                                       # 分析対象データの配置先
├── runs/                                         # 実行ごとの成果物
└── AGENTS.md                                     # IBM Bob への指示書
```

## 詳細仕様

- スキルの目的・完了条件・対象範囲: [.bob/skills/spss-modeler-baseline-automodel/SKILL.md](.bob/skills/spss-modeler-baseline-automodel/SKILL.md)
- Agent 全般のルール: [AGENTS.md](AGENTS.md)

## inputs/ 配下の取り扱いに関する注意

`inputs/` は git 追跡対象としているため、機微なデータ(顧客情報など)を配置する場合は事前に各自の `.gitignore` で除外することを推奨する。

## ライセンス

[MIT](LICENSE)
