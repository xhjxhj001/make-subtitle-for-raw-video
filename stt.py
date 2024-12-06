import whisper


class TransVoice:

    def __init__(self):
        print(whisper.available_models())
        # 可以根据情况替换成其他模型 ['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium',
        # 'large-v1', 'large-v2', 'large-v3', 'large']
        self.model = whisper.load_model("large-v3")

    def audio_to_text(self, audio_path):
        # 转换音频为文本
        transcription = self.model.transcribe(audio_path)

        return transcription
