from java.io import File
from java.io import FileInputStream, FileOutputStream
from java.io import OutputStreamWriter, BufferedWriter
from java.io import ByteArrayOutputStream
from java.nio import ByteBuffer
from java.nio.charset import Charset, CodingErrorAction
from jarray import array as jarray_array
from jarray import zeros as jarray_zeros

# ============================================================
# SPSS Modeler Baseline AutoModel - CSV Template
# Jython 2.x / SPSS Modeler Script
#
# 用途:
#   ベースライン自動モデル構築テンプレート。
#   タスク種別 (分類 / 数値予測 / クラスタリング) に応じて
#   autoclassifier / autonumeric / autocluster の 3 ノードを
#   切り替えて利用する。
#
# 出力形式:
#   全ての成果物 (sample / dataaudit / analysis / evaluation) を
#   HTML 形式で出力する。最終ファイルは UTF-8 BOM 付きへ変換する。
#
# 置換が必要な主な値:
#   - <INPUT_CSV_PATH>            入力 CSV の絶対パス
#   - <RUN_DIR>                   実行ディレクトリ (例 .../runs/run_xxx)
#   - <STREAM_FILENAME>           保存ストリームファイル名 (例 baseline.str)
#   - <INPUT_NODE_DISPLAY_NAME>   入力ノードの表示名
#   - <INPUT_ENCODING>            SystemDefault / UTF-8 / MS932 / Shift_JIS
#   - <DELIMITER>                 CSV 区切り文字 (例 ",")
#   - <FIELD_TYPES_ENTRIES>       type ノードの type 設定
#                                 例: u"年齢": u"Range", u"性別": u"Flag",
#   - <FIELD_VALUES_ENTRIES>      type ノードの values 設定 (Flag/Set 用)
#                                 例: u"性別": [u"F", u"M"],
#   - <FIELD_DIRECTIONS_ENTRIES>  type ノードの direction 設定
#                                 例: u"性別": u"Input", u"年収": u"Target",
#                                 (autocluster の場合は Target を含めない)
#   - <MODEL_NODE_TYPE>           "autoclassifier" / "autonumeric" / "autocluster"
#   - <MODEL_NODE_DISPLAY_NAME>   モデルノードの表示名 (自動分類/自動数値/自動クラスタリング 等)
#   - <MODEL_PROPS_ENTRIES>       モデルノードのプロパティ
#                                 例: "ranking_measure": u"Accuracy",
#                                     "number_of_models": 5,
#   - <INCLUDE_PARTITION>         "True" / "False" (autocluster は通常 False)
#   - <INCLUDE_ANALYSIS>          "True" / "False" (autocluster は通常 False)
#   - <INCLUDE_EVALUATION>        "True" / "False" (主に autoclassifier 向け)
# ============================================================


def ensure_dir(dir_path):
    d = File(dir_path)

    if not d.exists():
        ok = d.mkdirs()
        if not ok and not d.exists():
            raise Exception(u"[MKDIR_FAILED] directory could not be created: %s" % dir_path)

    if not d.isDirectory():
        raise Exception(u"[NOT_DIRECTORY] path is not directory: %s" % dir_path)


def require_file(path, label):
    f = File(path)

    if not f.exists():
        raise Exception(u"[MISSING_FILE] %s not found: %s" % (label, path))

    if not f.isFile():
        raise Exception(u"[INVALID_FILE] %s is not file: %s" % (label, path))


def require_created_file(path, label):
    f = File(path)

    if not f.exists():
        raise Exception(u"[OUTPUT_NOT_CREATED] %s not created: %s" % (label, path))

    if not f.isFile():
        raise Exception(u"[OUTPUT_INVALID] %s is not file: %s" % (label, path))

    if f.length() == 0:
        raise Exception(u"[OUTPUT_EMPTY] %s is empty: %s" % (label, path))


def set_props(node, props):
    for k, v in props.items():
        node.setPropertyValue(k, v)


def delete_file(path):
    f = File(path)
    if f.exists():
        ok = f.delete()
        if not ok and f.exists():
            raise Exception(u"[DELETE_FAILED] file could not be deleted: %s" % path)


def read_all_bytes(path):
    fis = FileInputStream(path)
    baos = ByteArrayOutputStream()
    buf = jarray_zeros(8192, 'b')

    try:
        n = fis.read(buf)
        while n != -1:
            baos.write(buf, 0, n)
            n = fis.read(buf)
        return baos.toByteArray()
    finally:
        fis.close()


def decode_bytes_strict(byte_data, encoding):
    decoder = Charset.forName(encoding).newDecoder()
    decoder.onMalformedInput(CodingErrorAction.REPORT)
    decoder.onUnmappableCharacter(CodingErrorAction.REPORT)
    return unicode(decoder.decode(ByteBuffer.wrap(byte_data)))


def detect_text_encoding(path):
    byte_data = read_all_bytes(path)

    encodings = [u"UTF-8", u"MS932", u"Windows-31J", u"Shift_JIS"]

    for enc in encodings:
        try:
            text = decode_bytes_strict(byte_data, enc)
            return enc, text
        except:
            pass

    return u"UTF-8", unicode(byte_data, "UTF-8", "replace")


def write_utf8_bom(path, text):
    fos = FileOutputStream(path)

    try:
        bom = jarray_array([-17, -69, -65], 'b')
        fos.write(bom)

        writer = BufferedWriter(OutputStreamWriter(fos, "UTF-8"))
        try:
            writer.write(text)
        finally:
            writer.close()
    finally:
        try:
            fos.close()
        except:
            pass


def convert_to_utf8_bom(src_path, dst_path):
    require_created_file(src_path, u"source file for UTF-8 BOM conversion")

    enc, text = detect_text_encoding(src_path)
    write_utf8_bom(dst_path, text)

    require_created_file(dst_path, u"converted UTF-8 BOM file")


def safe_filename(s):
    bad = u"\\/:*?\"<>| \t"
    out = []
    for ch in s:
        out.append(u"_" if ch in bad else ch)
    return u"".join(out)


phase = u"INIT"

try:
    # ------------------------------------------------------------
    # パス定義
    # ------------------------------------------------------------
    phase = u"パス定義"

    input_csv = u"<INPUT_CSV_PATH>"
    run_dir = u"<RUN_DIR>"
    stream_filename = u"<STREAM_FILENAME>"

    # run 配下の標準フォルダ構造
    #   scripts/  本 Jython 自身 (skill が配置・clemb 起動前に存在する)
    #   streams/  保存される .str
    #   outputs/  HTML 形式の実行成果物 (sample / dataaudit / analysis / evaluation)
    #   pmml/     構成モデルごとの PMML XML
    #   logs/     clemb_execution.log (skill が execute_clemb の log_file 引数で指定)
    output_dir = run_dir + u"/outputs"
    stream_dir = run_dir + u"/streams"
    pmml_output_dir = run_dir + u"/pmml"
    log_dir = run_dir + u"/logs"
    stream_path = stream_dir + u"/" + stream_filename

    # 最終出力先 (全て HTML 形式で統一)
    sample_output_path     = output_dir + u"/sample_baseline.html"
    dataaudit_output_path  = output_dir + u"/dataaudit_baseline.html"
    analysis_output_path   = output_dir + u"/analysis_baseline.html"
    evaluation_output_path = output_dir + u"/evaluation_baseline.html"

    # 一時 (変換前) 出力先 - SPSS から書き出された素のファイル
    tmp_sample_html     = output_dir + u"/_tmp_sample_baseline.html"
    tmp_dataaudit_html  = output_dir + u"/_tmp_dataaudit_baseline.html"
    tmp_analysis_html   = output_dir + u"/_tmp_analysis_baseline.html"
    tmp_evaluation_html = output_dir + u"/_tmp_evaluation_baseline.html"

    # 評価ブランチの ON/OFF (skill が "True"/"False" を埋める)
    include_partition  = (u"<INCLUDE_PARTITION>"  == u"True")
    include_analysis   = (u"<INCLUDE_ANALYSIS>"   == u"True")
    include_evaluation = (u"<INCLUDE_EVALUATION>" == u"True")

    # ------------------------------------------------------------
    # ディレクトリ作成・入力チェック
    # ------------------------------------------------------------
    phase = u"ディレクトリ作成"

    ensure_dir(output_dir)
    ensure_dir(stream_dir)
    ensure_dir(pmml_output_dir)
    ensure_dir(log_dir)

    phase = u"入力ファイル存在確認"

    require_file(input_csv, u"input_csv")

    # ------------------------------------------------------------
    # 前回実行結果削除
    # ------------------------------------------------------------
    phase = u"前回実行結果削除"

    delete_file(tmp_sample_html)
    delete_file(tmp_dataaudit_html)
    delete_file(tmp_analysis_html)
    delete_file(tmp_evaluation_html)
    delete_file(sample_output_path)
    delete_file(dataaudit_output_path)
    delete_file(analysis_output_path)
    delete_file(evaluation_output_path)

    # ------------------------------------------------------------
    # ストリーム取得
    # ------------------------------------------------------------
    phase = u"ストリーム取得"

    stream = modeler.script.stream()
    stream.setPropertyValue("encoding", u"UTF-8")

    # ------------------------------------------------------------
    # Step 1: 入力 CSV ノード (variablefile)
    # ------------------------------------------------------------
    phase = u"Step 1: variablefile_node"

    variablefile_node = stream.createAt("variablefile", u"<INPUT_NODE_DISPLAY_NAME>", 80, 100)
    set_props(variablefile_node, {
        "full_filename": input_csv,
        "read_field_names": True,
        "delimit_other": True,
        "other": u"<DELIMITER>",
        "decimal_symbol": u"Period",
        "encoding": u"<INPUT_ENCODING>"
    })

    # ------------------------------------------------------------
    # Step 2: 型定義 (type)
    # フィールド毎の type / values / direction を設定する
    # 中身は skill がデータに合わせて埋める
    # 空辞書のままなら type ノードはモデラ側の自動推定に委ねる
    # ------------------------------------------------------------
    phase = u"Step 2: type_node"

    type_node = stream.createAt("type", u"型定義", 220, 100)

    field_types = {
        # <FIELD_TYPES_ENTRIES>
    }
    for field, ftype in field_types.items():
        type_node.setKeyedPropertyValue("type", field, ftype)

    field_values = {
        # <FIELD_VALUES_ENTRIES>
    }
    for field, vlist in field_values.items():
        type_node.setKeyedPropertyValue("values", field, vlist)

    field_directions = {
        # <FIELD_DIRECTIONS_ENTRIES>
    }
    for field, direction in field_directions.items():
        type_node.setKeyedPropertyValue("direction", field, direction)

    # ------------------------------------------------------------
    # Step 2.5: データ監査 (dataaudit) → HTML
    # display_graphs=True で各変数の分布サムネイルグラフを HTML 内に出力する
    # ------------------------------------------------------------
    phase = u"Step 2.5: dataaudit_node"

    dataaudit_node = stream.createAt("dataaudit", u"データ監査", 220, 240)
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

    # ------------------------------------------------------------
    # Step 2.6: サンプリング (sample) - 先頭 10 行
    # ------------------------------------------------------------
    phase = u"Step 2.6: sample_node"

    sample_node = stream.createAt("sample", u"サンプリング", 80, 240)
    set_props(sample_node, {
        "method": u"Simple",
        "mode": u"Include",
        "sample_type": u"First",
        "first_n": 10
    })

    # ------------------------------------------------------------
    # Step 2.7: テーブル (table) - サンプル HTML 出力
    # ------------------------------------------------------------
    phase = u"Step 2.7: table_node"

    table_node = stream.createAt("table", u"テーブル", 80, 360)
    set_props(table_node, {
        "output_mode": u"File",
        "output_format": u"HTML",
        "full_filename": tmp_sample_html
    })

    # ------------------------------------------------------------
    # Step 3: パーティション (autocluster の場合は不要)
    # ------------------------------------------------------------
    partition_node = None

    if include_partition:
        phase = u"Step 3: partition_node"

        partition_node = stream.createAt("partition", u"パーティション", 360, 100)
        set_props(partition_node, {
            "create_validation": False,
            "training_size": 70,
            "testing_size": 30,
            "set_random_seed": True,
            "random_seed": 12345
        })

    # ------------------------------------------------------------
    # Step 4: 自動モデルノード
    # autoclassifier / autonumeric / autocluster のいずれかを skill が選択
    # ------------------------------------------------------------
    phase = u"Step 4: model_node"

    model_node = stream.createAt(u"<MODEL_NODE_TYPE>", u"<MODEL_NODE_DISPLAY_NAME>", 500, 60)
    set_props(model_node, {
        # <MODEL_PROPS_ENTRIES>
    })

    # ------------------------------------------------------------
    # Step 5: ノードのリンク (構築側)
    # ------------------------------------------------------------
    phase = u"Step 5: ノードのリンク"

    stream.link(variablefile_node, type_node)
    stream.link(type_node, dataaudit_node)
    stream.link(type_node, sample_node)
    stream.link(sample_node, table_node)

    if partition_node is not None:
        stream.link(type_node, partition_node)
        stream.link(partition_node, model_node)
    else:
        stream.link(type_node, model_node)

    # ------------------------------------------------------------
    # Step 6: ストリーム保存
    # ------------------------------------------------------------
    phase = u"Step 6: ストリーム保存"

    taskrunner = modeler.script.session().getTaskRunner()
    taskrunner.saveStreamToFile(stream, stream_path)
    require_created_file(stream_path, u"saved stream file")

    # ------------------------------------------------------------
    # Step 7: モデル構築実行
    # ------------------------------------------------------------
    phase = u"Step 7: モデル構築実行"

    model_results = []
    model_node.run(model_results)

    if len(model_results) == 0:
        raise Exception(u"model_node の実行結果にモデルが含まれていません")

    model_output = model_results[0]

    # ------------------------------------------------------------
    # Step 7.1: 構成モデルごとの PMML XML を出力
    # IBM 公式例では FileFormat.XML の出力ファイルに .xml 拡張子を使用している。
    # FileFormat.XML は PMML の XML 形式を出力するため、拡張子も .xml に合わせる。
    # 複合モデル (autoclassifier 等) は内部で複数アルゴリズムを束ねるため、
    # 個別モデルを 1 つずつ取り出して保存する。
    # 失敗するコンポーネントはスキップして処理を続行する。
    # ------------------------------------------------------------
    phase = u"Step 7.1: 構成モデル PMML XML 出力"

    import modeler.api

    composite_detail = None
    iterator = None
    try:
        composite_detail = model_output.getModelDetail()
        iterator = composite_detail.getIndividualModelResults()
    except Exception, ex_iter:
        print u"[WARN] getIndividualModelResults failed: %s" % unicode(str(ex_iter), errors='ignore')

    exported = []
    skipped  = []

    idx = 0
    if iterator is not None:
        while iterator.hasNext():
            idx += 1
            component = iterator.next()

            try:
                model_name = unicode(component.getModelName())
            except Exception:
                model_name = u"model_%d" % idx
            label = safe_filename(model_name) if model_name else (u"model_%d" % idx)
            out_path = u"%s/%02d_%s.xml" % (pmml_output_dir, idx, label)

            try:
                individual_output = component.getModelOutput()
                if individual_output is None:
                    skipped.append((model_name, u"getModelOutput returned None"))
                else:
                    taskrunner.exportModelToFile(individual_output, out_path, modeler.api.FileFormat.XML)
                    exported.append((model_name, out_path))
            except Exception, ex_each:
                skipped.append((model_name, unicode(str(ex_each), errors='ignore')))

    print u"[INFO] PMML XML exported: %d, skipped: %d" % (len(exported), len(skipped))
    for name, p in exported:
        print u"  EXPORT %s -> %s" % (name, p)
    for name, msg in skipped:
        print u"  SKIP   %s: %s" % (name, msg)

    # ------------------------------------------------------------
    # Step 8: 生成モデルの適用ノードを作成
    # ------------------------------------------------------------
    phase = u"Step 8: モデル適用ノード作成"

    model_applier_node = stream.createModelApplierAt(model_output, u"ベースラインモデル適用", 650, 100)
    try:
        model_applier_node.setPropertyValue("filter_individual_model_output", False)
    except Exception, ex_filter:
        print u"[WARN] filter_individual_model_output set failed: %s" % unicode(str(ex_filter), errors='ignore')

    # ------------------------------------------------------------
    # Step 9: 評価系ノード (analysis / evaluation)
    # autocluster の場合はどちらも作成しない設定にする
    # ------------------------------------------------------------
    analysis_node = None
    evaluation_node = None

    if include_analysis:
        phase = u"Step 9-1: analysis_node"

        analysis_node = stream.createAt("analysis", u"精度分析", 820, 60)
        set_props(analysis_node, {
            "coincidence": True,
            "performance": True,
            "confidence": True,
            "output_mode": "File",
            "output_format": "HTML",
            "full_filename": tmp_analysis_html
        })

    if include_evaluation:
        phase = u"Step 9-2: evaluation_node"

        evaluation_node = stream.createAt("evaluation", u"評価グラフ", 820, 140)
        set_props(evaluation_node, {
            "chart_type": "Gains",
            "inc_baseline": True,
            "inc_best_line": True,
            "output_mode": "File",
            "output_format": "HTML",
            "full_filename": tmp_evaluation_html
        })

    # ------------------------------------------------------------
    # Step 10: 評価用ブランチのリンク
    # ------------------------------------------------------------
    phase = u"Step 10: 評価用ブランチのリンク"

    if partition_node is not None:
        stream.link(partition_node, model_applier_node)
    else:
        stream.link(type_node, model_applier_node)

    if analysis_node is not None:
        stream.link(model_applier_node, analysis_node)

    if evaluation_node is not None:
        stream.link(model_applier_node, evaluation_node)

    # ------------------------------------------------------------
    # Step 11: 末端ノード実行
    # ------------------------------------------------------------
    phase = u"Step 11-1: dataaudit 実行"
    dataaudit_node.run([])
    require_created_file(tmp_dataaudit_html, u"dataaudit raw html")

    phase = u"Step 11-2: table (sample) 実行"
    table_node.run([])
    require_created_file(tmp_sample_html, u"sample raw html")

    if analysis_node is not None:
        phase = u"Step 11-3: analysis 実行"
        analysis_node.run([])
        require_created_file(tmp_analysis_html, u"analysis raw html")

    if evaluation_node is not None:
        phase = u"Step 11-4: evaluation 実行"
        evaluation_node.run([])
        require_created_file(tmp_evaluation_html, u"evaluation raw html")

    # ------------------------------------------------------------
    # Step 12: 出力 HTML を BOM 付き UTF-8 へ変換
    # ブラウザは BOM を charset 宣言より優先するため、
    # ソース HTML 内の meta charset 宣言が異なっていても表示は崩れない。
    # ------------------------------------------------------------
    phase = u"Step 12-1: dataaudit HTML を UTF-8 BOM へ変換"
    convert_to_utf8_bom(tmp_dataaudit_html, dataaudit_output_path)
    delete_file(tmp_dataaudit_html)

    phase = u"Step 12-2: sample HTML を UTF-8 BOM へ変換"
    convert_to_utf8_bom(tmp_sample_html, sample_output_path)
    delete_file(tmp_sample_html)

    if analysis_node is not None:
        phase = u"Step 12-3: analysis HTML を UTF-8 BOM へ変換"
        convert_to_utf8_bom(tmp_analysis_html, analysis_output_path)
        delete_file(tmp_analysis_html)

    if evaluation_node is not None:
        phase = u"Step 12-4: evaluation HTML を UTF-8 BOM へ変換"
        convert_to_utf8_bom(tmp_evaluation_html, evaluation_output_path)
        delete_file(tmp_evaluation_html)

    # ------------------------------------------------------------
    # Step 13: モデル適用・評価ノード付きストリームを再保存
    # ------------------------------------------------------------
    phase = u"Step 13: 評価付きストリーム再保存"

    taskrunner.saveStreamToFile(stream, stream_path)


except Exception, e:
    raise Exception(u"[SPSS_JYTHON_FAILED] phase=%s error_type=%s error=%s" % (
        phase,
        e.__class__.__name__,
        unicode(str(e), errors='ignore')
    ))
