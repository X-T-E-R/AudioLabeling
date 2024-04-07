from funasr import AutoModel
import os




class Audio2Emotion():
    def __init__(self, models_path="",  **kwargs):
        def join_models_path(model_name):
            if os.path.exists(os.path.join(models_path, model_name)):
                return os.path.join(models_path, model_name)
            else:
                return model_name
        if models_path[-1] == "/":
            models_path = models_path[:-1]
        if models_path.endswith("iic"):
            models_path = models_path[:-3]
        self.main_model = kwargs.get("model", "iic/emotion2vec_base_finetuned")

        if models_path != "":
            self.main_model = join_models_path(self.main_model)

        kwargs.update({"model": self.main_model})
        # print(kwargs)

        self.model = AutoModel(**kwargs)
        self.loaded = True
    
    def vec2emotion(self, emotion_vec):
        if isinstance(emotion_vec, list):
            emotion_vec = emotion_vec[0]
        assert isinstance(emotion_vec, dict)
        labels = emotion_vec["labels"]
        scores = emotion_vec["scores"]
        sorted_emotions = sorted(zip(labels, scores), key=lambda x: x[1], reverse=True)
        return sorted_emotions[0][0]
        
    def get_emotion_vec(self, audio_path, granularity="utterance", extract_embedding=False, output_dir="./Outputs/emotion_embedding", **kwargs):
        res = self.model.generate(audio_path,  granularity=granularity, extract_embedding=extract_embedding, output_dir=output_dir, **kwargs)
        return res
    
    def get_emotion(self, audio_path, return_vec=False, **kwargs):
        emotion_vec = self.get_emotion_vec(audio_path, **kwargs)
        emotion = self.vec2emotion(emotion_vec)
        if return_vec:
            return emotion, emotion_vec
        else:
            return emotion
        
    def __enter__(self):
        # 这里可以添加进入 with 语句时需要执行的代码
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 这里可以添加退出 with 语句时需要执行的代码
        pass



if __name__ == "__main__":
    audio_to_srt = Audio2Emotion(models_path=r"E:\AItools\AudioLabeling\models")

    audios_path = r"E:\AIDB\花火\refer_audio"
    audio_list = [os.path.join(audios_path, i) for i in os.listdir(audios_path) if i.lower().endswith(".wav")]
    for audio_path in audio_list:
        emotion = audio_to_srt.get_emotion(audio_path=audio_path)
        print(f"{audio_path} : {emotion}")