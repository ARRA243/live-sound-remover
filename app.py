from flask import Flask, request, render_template, send_from_directory
import os
import ffmpeg
from spleeter.separator import Separator

app = Flask(__name__)

# index.htmlを表示する
@app.route('/')
def home():
    return render_template('index.html') 

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return "ファイルが見つかりません。"

        file = request.files['file']
        if file.filename == '':
            return "ファイルが選択されていません。"

        input_file = "uploaded_video.mp4"  # アップロードされたファイルの保存名
        file.save(input_file)  # ファイルを保存する

        # 音声分離の処理
        output_directory = 'output/'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # 音を2つ（声とゲーム音）に分ける
        separator = Separator('spleeter:2stems')
        separator.separate_to_file(input_file, output_directory)

        # 分けた音声ファイルのパスを設定
        vocals_file = os.path.join(output_directory,
                                   "uploaded_video/vocals.wav")

        # ffmpeg-pythonで声だけの動画を作成
        global final_output_file  # グローバル変数としてfinal_output_fileを設定
        final_output_file = "final_video.mp4"

        video_stream = ffmpeg.input(input_file).video  # 映像ストリームのみ取得
        audio_stream = ffmpeg.input(vocals_file).audio  # 音声ストリームのみ取得

        (
            ffmpeg
            .output(video_stream, audio_stream, final_output_file,
                    vcodec='copy',
                    acodec='aac')
            .run(overwrite_output=True)
        )

        return "声だけの動画が作成されました！<br><a href='/download'>ダウンロードする</a>"

    except Exception as e:
        return f"エラーが発生しました: {str(e)}"  # エラーメッセージを表示


@app.route('/download')
def download_file():
    return send_from_directory(directory='.', path=final_output_file,
                               as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
