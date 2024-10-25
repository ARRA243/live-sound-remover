import os
import subprocess
from spleeter.separator import Separator
import tensorflow as tf

def main():
    # MP4ファイルのパスと、出力する音声ファイルの名前を設定
    input_file = "archive_video.mp4"  # もらったMP4ファイルの名前
    output_audio = "audio.wav"          # 抜き出す音声のファイル名（wav形式）

    # FFmpegを使ってMP4から音声を抜き出す（-yオプションを追加）
    subprocess.run(["ffmpeg", "-y", "-i", input_file, "-b:a", "128k", "-map", "a", output_audio])

    # 音を2つ（声とその他）に分けるためのツールを準備
    separator = Separator('spleeter:2stems')

    # 出力先のディレクトリを作成（存在しない場合）
    output_directory = 'output/'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # 音を分ける
    separator.separate_to_file(output_audio, output_directory)

    # 分けた音声ファイルのパスを設定
    vocals_file = os.path.join(output_directory, "audio/vocals.wav")
    accompaniment_file = os.path.join(output_directory, "audio/accompaniment.wav")

    # 元動画と声の音声を組み合わせる
    final_output_file = "final_video.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-i", input_file, "-i", vocals_file, "-c:v", "copy",
         "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", final_output_file])

    print(f"最終動画ファイルが作成されました: {final_output_file}")

if __name__ == '__main__':
    main()
