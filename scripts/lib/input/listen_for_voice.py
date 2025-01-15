import wave
import pyaudio
import webrtcvad
import openai
from config import logging, OPENAI_API_KEY
import os

openai.api_key = OPENAI_API_KEY

# --- 基本設定 ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_DURATION_MS = 20  # 1 フレーム 20ms
CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000)  # 320 サンプル
SILENCE_DURATION = 3.0  # 無音とみなす時間 (秒)

# VAD の感度レベル (0~3)。高いほど厳密に判定するが、誤検出が増える場合もある。
VAD_MODE = 3

p = pyaudio.PyAudio()

def remove_silence(frames, vad, sample_rate):
    """
    音声データから無音部分を削除
    frames: 音声フレームのリスト
    vad: WebRTC VAD オブジェクト
    sample_rate: サンプルレート
    """
    non_silent_frames = []

    for frame in frames:
        if vad.is_speech(frame, sample_rate):
            non_silent_frames.append(frame)

    return non_silent_frames

def record_audio_vad():
    """
    WebRTC VAD を利用して音声を録音し、無音状態が一定時間続いたら録音を終了する
    """
    vad = webrtcvad.Vad(VAD_MODE)

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )

    print("録音開始...")

    frames = []
    silent_chunks = 0
    # SILENCE_DURATION に基づいて、何フレーム連続で無音なら終了するか
    # 例えば 1 秒分無音で終了なら、1.0s / 0.02s = 50 フレーム
    silence_chunk_limit = int(SILENCE_DURATION / (CHUNK_DURATION_MS / 1000.0))

    while True:
        data = stream.read(CHUNK_SIZE)
        # 16bit モノラル、リトルエンディアンを想定
        # WebRTC VAD は 16kHz, 16bit, モノラル, リトルエンディアンのみ対応
        is_speech = vad.is_speech(data, sample_rate=RATE)

        frames.append(data)

        if not is_speech:
            silent_chunks += 1
        else:
            silent_chunks = 0

        # 一定フレーム数連続で音声なしと判定されたら録音終了
        if silent_chunks > silence_chunk_limit:
            break

    print("録音終了")

    stream.stop_stream()
    stream.close()

    # 無音部分を削除
    processed_frames = remove_silence(frames, vad, RATE)

    # 音声を一時ファイルに保存
    filename = "processed_audio.wav"
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(processed_frames))
    wf.close()

    return filename

def transcribe_audio(filename, min_file_size_kb=1):
    """
    Whisper API で音声をテキストに変換
    """
    if os.path.getsize(filename) < min_file_size_kb * 1024:
        return ""
    with open(filename, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
            language="ja"
        )

        return transcript
def listen_for_voice(data_handler=None, min_file_size_kb=10):
    """
    音声入力を受け取る関数
    """
    if data_handler is None:
        raise ValueError("data_handler が指定されていません")

    while True:
        # 音声録音 (VAD 実装版)
        audio_file = record_audio_vad()

        # 音声認識
        instr = transcribe_audio(audio_file, min_file_size_kb)

        logging.error(instr)

        # 空文字 (無音など) の場合は終了
        if not instr:
            break

        # 発話内容を data_handler に渡して応答を生成
        outstr = data_handler(instr)
        print(f"SYNTH_START|0|mei_voice_normal|{outstr}")

# 使用例
def example_handler(text):
    return f"あなたはこう言いました: {text}"
