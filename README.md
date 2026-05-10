# SPSS Modeler Baseline AutoModel Skill

SPSS Modeler でベースライン自動モデル(`.str`)を作るための、IBM Bob 用スキルとエージェント定義をまとめたリポジトリ。

CSV 等の入力データを与えると、IBM Bob が Jython スクリプトを生成・実行し、データ確認 → AutoModel(分類 / 数値予測 / クラスタリング)→ PMML 出力 → 評価 → ストリーム保存までを 1 本のフローで完結させる。

## 動作環境

- Windows
- Python 3.10 以上(必須。未インストールでは動作しない)
- SPSS Modeler 19.0(必須。未インストールでは動作しない)
- Jython 2.7(SPSS Modeler に内包)
- IBM Bob

## 依存 MCP サーバ

本リポジトリ単体では動作せず、以下 2 つの MCP サーバを別途セットアップする必要がある。セットアップ手順は各リポジトリのページを参照。

| 名前 | 用途 | 入手先 |
|---|---|---|
| `spss-clemb-mcp` | SPSS Modeler の `clemb` 経由で Jython を実行 | <https://github.com/hkwd/spss-clemb-mcp> |
| `ibm-docs-mcp` | SPSS Modeler ノード仕様の裏取り | <https://github.com/hkwd/ibm-docs-mcp> |

## セットアップ

1. 本リポジトリを clone する
2. 上記 2 つの MCP サーバを、各リポジトリのページに記載された手順でセットアップする
3. [.bob/mcp_settings.json](.bob/mcp_settings.json) を開き、2 箇所の `<path-to-...>` を実際の MCP サーバ配置パスに書き換える
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
│   ├── mcp_settings.json                         # MCP 接続定義
│   └── skills/
│       └── spss-modeler-baseline-automodel/      # 主スキル本体
│           ├── SKILL.md                          # スキルの目的・完了条件・フロー定義
│           ├── phase2-summary-report.md          # フェーズ 2 サマリーレポートの仕様
│           ├── _shared/                          # 共通ユーティリティ
│           └── templates/                        # Jython / レポートのテンプレート
├── inputs/                                       # 分析対象データの配置先
├── runs/                                         # 実行ごとの成果物
└── AGENTS.md                                     # IBM Bob への指示書
```

## 詳細仕様

- スキルの目的・完了条件・対象範囲: [.bob/skills/spss-modeler-baseline-automodel/SKILL.md](.bob/skills/spss-modeler-baseline-automodel/SKILL.md)
- Agent 全般のルール: [AGENTS.md](AGENTS.md)

## inputs/ 配下の取り扱いに関する注意

`inputs/` は git 追跡対象としているため、機微なデータ(顧客情報など)を配置する場合は事前に各自の `.gitignore` で除外することを推奨する。

## 注意事項
本リポジトリは現在テスト段階のものです。動作保証はありません。本番環境での利用は想定していません。ご利用の際は、検証環境等で十分にテストしたうえで、自己責任でご利用ください。


Made with Bob