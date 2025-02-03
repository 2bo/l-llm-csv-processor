# Local LLM CSV Processor

このプロジェクトは、同じプロンプトを複数のデータに対して実行したい場合に便利なツールです。CSV ファイル内の複数の入力文（'text' カラム）に対して、一つのシステムプロンプトを使って生成AI（LLM）に一括で指示を送り、その応答を取得します。  
Python の標準ライブラリを利用して CSV を堅牢に処理し、Ollama CLI 経由で LLM（デフォルト: phi4 モデル）へプロンプトを送信します。

主な機能:
- CSV ファイルから 'text' カラムの入力文を一括読み取り
- 一つのプロンプトを全データに適用（コマンドライン引数またはファイルから指定可能）
- 各入力文に対する LLM の応答を自動で取得
- すべての入力と応答のペアを CSV ファイルに保存し、処理結果を一覧表示

例えば、多数の日本語文を英訳したい場合や、複数の文章を要約したい場合など、同じ処理を複数のテキストに適用する際に効率的です。

## セットアップ手順

### 1. Ollamaのインストールと設定

1. macOSの場合、Homebrewを使用してOllamaをインストールします：

   ```bash
   brew install ollama
   ```

   または、Linux/WSLの場合は以下のコマンドでインストール：

   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. Ollamaサービスを起動します：

   ```bash
   ollama serve
   ```

3. 別のターミナルで、phi4モデルをダウンロードします：

   ```bash
   ollama pull phi4
   ```

   > Note: モデルのダウンロードには時間がかかる場合があります。

### 2. GitHub リポジトリのクローン

1. GitHub 上でこのリポジトリ（例: `llm-csv-processor`）を作成または公開されているリポジトリをクローンします。

   ```bash
   git clone https://github.com/2bo/l-llm-csv-processor.git
   cd l-llm-csv-processor
   ```

### 2. Python 仮想環境 (venv) のセットアップ

1. リポジトリのルートで仮想環境を作成します。

   ```bash
   python3 -m venv venv
   ```

2. 仮想環境をアクティベートします。

   ```bash
   source venv/bin/activate
   ```

3. 必要なパッケージをインストールします（現時点では標準ライブラリのみ使用しているため追加パッケージは不要です）。

### 3. CSV ファイルの準備

1. リポジトリ内に入力用 CSV ファイル（例: `input.csv`）を作成してください。  
   CSV ファイルはヘッダー行が必要で、対象カラムは `text` とします。  
   例:

   ```csv
   text
   The weather is beautiful today.
   I love spending time with my family.
   She works at a local coffee shop.
   The children are playing in the park.
   ```

## 使用方法

1. 仮想環境をアクティベートした状態で、Python スクリプト `l_llm_csv_processor.py` を実行します。
   プロンプトは直接指定するか、ファイルから読み込むことができます。

   ```bash
   # プロンプトを直接指定する場合
   python3 l_llm_csv_processor.py -f sample-input.csv -p "日本語訳してください:"

   # プロンプトをファイルから読み込む場合
   python3 l_llm_csv_processor.py -f sample-input.csv -P sample-prompt.txt
   ```

   オプション:
   - `-f, --file`: 入力CSVファイルのパス（必須）
   - `-p, --prompt`: LLMへのプロンプト文字列
   - `-P, --prompt-file`: プロンプトを含むファイルのパス
   - `-o, --output`: 出力CSVファイルのパス（省略時は入力ファイル名に '_result' を追加）
   - `-m, --model`: 使用するLLMモデル名（デフォルト: phi4）

2. スクリプトは CSV 内の各行を読み込み、各入力文に対して以下の形式のプロンプトを生成します。

   ```
   <システムプロンプト>

   --- 以下の入力文 ---
   <CSV からの入力文>
   --- 以上 ---
   ```

3. 生成されたプロンプトが `ollama run phi4` を介して phi4 モデルに送信され、応答が取得されます。  
   処理結果は以下の形式で保存・出力されます：
   - 指定された出力CSVファイル（または入力ファイル名_result.csv）に保存
   - コンソールに各入力文と対応する応答を表示


## 注意事項

- 本スクリプトは、Ollama CLI がインストール済みで PATH に追加され、phi4 モデルがローカルで利用可能な状態であることを前提としています。phi4以外のモデルを使用する場合は、`-m` オプションで指定してください。
- プロンプトの構造は、タスクに応じて適宜調整してください（例えば、翻訳以外の処理や、より複雑な指示の場合）。
- 出力CSVファイルには、入力文（input）と応答（response）の2つのカラムが含まれます。
