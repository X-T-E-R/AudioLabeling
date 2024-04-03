from funasr import AutoModel
import os


class Res2SRT:
    @staticmethod
    def time_convert(ms):
        ms = int(ms)
        tail = ms % 1000
        seconds = ms // 1000
        minutes = seconds // 60
        seconds %= 60
        hours = minutes // 60
        minutes %= 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{tail:03d}"

    def format_text(self, text):
        formatted_text = ""
        for word in text.split():
            if '\u4e00' <= word <= '\u9fff':
                formatted_text += word
            else:
                formatted_text += " " + word
        return formatted_text.strip()

    def generate_srt(self, res, offset=0):
        if isinstance(res, list):
            res = res[0]
        assert isinstance(res, dict)
        srt_total = ''
        for i, d in enumerate(res["sentence_info"]):
            start, end = d['timestamp'][0][0] - offset, d['timestamp'][-1][1] - offset
            start_time = self.time_convert(start)
            end_time = self.time_convert(end)
            text = self.format_text(d['text'])

            if 'spk' in d:
                srt_total += f"{i+1}  spk{d['spk']}\n{start_time} --> {end_time}\n{text}\n\n"
            else:
                srt_total += f"{i+1}\n{start_time} --> {end_time}\n{text}\n\n"
        return srt_total

class Audio2Srt():
    def __init__(self, models_path="",  allow_spk = False,  **kwargs):
        def join_models_path(model_name):
            if os.path.exists(os.path.join(models_path, model_name)):
                return os.path.join(models_path, model_name)
            else:
                return model_name
            
        
        main_model = kwargs.get("model", "paraformer-zh")
        vad_model = kwargs.get("vad_model", "fsmn-vad")
        punc_model= kwargs.get("punc_model", "ct-punc")
        spk_model = kwargs.get("spk_model", "cam++")
        
        if models_path != "":
            self.main_model = join_models_path(main_model)
            self.vad_model = join_models_path(vad_model)
            self.punc_model = join_models_path(punc_model)
            self.spk_model = join_models_path(spk_model)
        
        if not allow_spk:
            self.spk_model = None
        # if not allow_punc:
        #     self.punc_model = None
        kwargs.update({"model": self.main_model, "vad_model": self.vad_model, "punc_model": self.punc_model, "spk_model": self.spk_model})
        self.model = AutoModel(**kwargs)
        self.res2srt = Res2SRT()
        self.loaded = True

    def transcribe(self, audio_path, **kwargs):
        language = kwargs.get("language", None)
        batch_size_s = kwargs.get("batch_size_s", 0)
        
        kwargs.update({"input": audio_path, "language": language,"task":"transcribe", "sentence_timestamp" :True})
        
        res = self.model.generate(**kwargs)
        return res
    
    def generate_srt(self, audio_path, **kwargs):
        return self.res2srt.generate_srt(self.transcribe(audio_path, **kwargs))

if __name__ == "__main__":
    audio_to_srt = Audio2Srt(models_path=r"E:\AItools\AudioLabeling\models\iic", allow_spk=True)

    audio_paths = [r"C:\Users\xxoy1\OneDrive\桌面\music rebalance\「荒野会谈」第一期 人可以完全没有社交吗 - 1.第一期 人可以完全没有社交吗(Av818072525,P1).mp3"
    ,r"E:\AIDB\夏青杂交\23 朗诵：白居易《琵琶行》并序.mp3"]
    for audio_path in audio_paths:
        filename = os.path.basename(audio_path).rsplit(".", 1)[0]

        res = audio_to_srt.generate_srt(audio_path)
        with open(f"{filename}.srt", "w", encoding="utf-8") as f:
            f.write(res)