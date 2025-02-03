#!/usr/bin/env python3
import csv
import subprocess
import argparse
import sys

def call_llm(prompt: str, model: str) -> str:
    """
    指定されたプロンプトを生成AI（LLM）へ送信し、応答を取得する。
    Ollama CLI が PATH に存在し、指定されたモデルが利用可能な状態であることを前提とする。
    """
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Error running ollama: {e.stderr}\n")
        return ""

def main():
    parser = argparse.ArgumentParser(
        description="CSV 内の入力文（'text' カラム）とシステムプロンプトを統合してLLMへ指示を送信し、応答を取得するツールです。"
    )
    parser.add_argument(
        "-f", "--file",
        required=True,
        help="入力 CSV ファイルのパス（ヘッダー行があり、対象カラムは 'text'）"
    )
    
    # プロンプトの指定方法をグループ化
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument(
        "-p", "--prompt",
        help="LLM へのプロンプト（例: '以下の日本語を英訳してください:'）"
    )
    prompt_group.add_argument(
        "-P", "--prompt-file",
        help="プロンプトを含むファイルのパス"
    )
    
    parser.add_argument(
        "-o", "--output",
        required=False,
        help="出力 CSV ファイルのパス（省略時は入力ファイル名に '_result' を追加）"
    )
    parser.add_argument(
        "-m", "--model",
        default="phi4",
        help="使用するLLMモデル名（デフォルト: phi4）"
    )
    args = parser.parse_args()

    csv_file = args.file
    
    # プロンプトの取得
    if args.prompt:
        system_prompt = args.prompt
    else:
        try:
            with open(args.prompt_file, 'r', encoding='utf-8') as f:
                system_prompt = f.read().strip()
        except FileNotFoundError:
            sys.stderr.write(f"Error: プロンプトファイル '{args.prompt_file}' が見つかりません。\n")
            sys.exit(1)
        except PermissionError:
            sys.stderr.write(f"Error: プロンプトファイル '{args.prompt_file}' を読み取る権限がありません。\n")
            sys.exit(1)
    
    model = args.model
    
    # 出力ファイル名の生成
    if args.output:
        output_file = args.output
    else:
        # 入力ファイル名から拡張子を分離
        base_name = csv_file.rsplit('.', 1)[0]
        output_file = f"{base_name}_result.csv"

    # CSV ファイルの存在チェック
    try:
        with open(csv_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "text" not in reader.fieldnames:
                sys.stderr.write("Error: CSV に 'text' カラムが存在しません。\n")
                sys.exit(1)
            # 結果を格納するリスト
            responses = []
            # CSV の各行を処理
            for row in reader:
                input_text = row.get("text", "").strip()
                if not input_text:
                    continue

                # プロンプトの構造を明確にするために区切りを追加
                prompt = f"""{system_prompt}

--- 以下の入力のみを対象として応答してください---
{input_text}
--- 以上 ---
"""
                print(f"処理中: {input_text}")
                response = call_llm(prompt, model)
                responses.append({
                    "input": input_text,
                    "response": response
                })

        # 結果をCSVファイルに出力
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['input', 'response'])
            writer.writeheader()
            writer.writerows(responses)

        # 結果の表示
        print(f"\n結果を {output_file} に保存しました。")
        print("\n=== LLM からの応答一覧 ===")
        for idx, res in enumerate(responses, start=1):
            print(f"【文 {idx}】")
            print(f"  入力文: {res['input']}")
            print(f"  応答  : {res['response']}")
            print("")

    except FileNotFoundError:
        sys.stderr.write(f"Error: ファイル '{csv_file}' が見つかりません。\n")
        sys.exit(1)
    except PermissionError:
        sys.stderr.write(f"Error: 出力ファイル '{output_file}' に書き込み権限がありません。\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
