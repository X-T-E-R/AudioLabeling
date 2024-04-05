import sys,os
sys.path.append(".")

from tools.my_utils import scan_ext_walk, scan_audios_walk
from tools._3d_speaker.cluster import CommonClustering
from funasr import AutoModel
import os
import pickle
import numpy as np

class Audio2Embedding():
    def __init__(self, models_path="",  **kwargs):
        def join_models_path(model_name):
            if os.path.exists(os.path.join(models_path, model_name)):
                return os.path.join(models_path, model_name)
            else:
                return model_name
        self.main_model = kwargs.get("model", "cam++")

        if models_path != "":
            self.main_model = join_models_path(self.main_model)

        kwargs.update({"model": self.main_model})
        # print(kwargs)

        self.model = AutoModel(**kwargs)
        self.loaded = True

    def get_embedding(self, audio_path, audio_list, save_embedding=True, embedding_type="cam++", **kwargs):
        if isinstance(audio_list, str):
            audio_list = [audio_list]
        pickle_file_path = os.path.join(audio_path, f"spk_embedding({embedding_type}).pkl")
        existed_embeddings = []
        if os.path.exists(pickle_file_path):
            with open(pickle_file_path, "rb") as f:
                existed_embeddings = pickle.load(f)
        for item in existed_embeddings:
            if item["file_path"] in audio_list:
                audio_list.remove(item["file_path"])
        if len(audio_list) != 0:
            result = self.model.generate(
                [os.path.join(audio_path, audio_file) for audio_file in audio_list]
            )
            for audio_file, embedding in zip(audio_list, result):
                existed_embeddings.append(
                    {
                        "file_path": audio_file,
                        "spk_embedding": embedding["spk_embedding"],
                    }
                )
            if save_embedding:
                with open(pickle_file_path, "wb") as f:
                    pickle.dump(existed_embeddings, f)
        return existed_embeddings


class SpeakerClassifier():
    def __init__(self, models_path="", **kwargs):
        
        self.audio2embedding = Audio2Embedding(**kwargs)
        self.loaded = True
    
    def generate(self, audio_path, cluster_name="spectral", min_num_spks=1, max_num_spks=10, output_type="list", **kwargs):
        cluster = CommonClustering(cluster_type=cluster_name, mer_cos=None, min_num_spks=min_num_spks, max_num_spks=max_num_spks)
        audio_list = scan_audios_walk(audio_path)
        result = self.audio2embedding.get_embedding(audio_path, audio_list)
        auduo_files = [item["file_path"] for item in result]
        spk_embeddings = [item["spk_embedding"] for item in result]
        
        # 使用np.concatenate()函数将所有张量连接成一个新的张量
        concatenated_array = np.concatenate([x.cpu().numpy() for x in spk_embeddings], axis=0)
        # 使用np.stack()函数将连接后的张量转换为形状为 [N, C] 的张量
        final_array = np.stack(concatenated_array, axis=0)

        labels = cluster.__call__(final_array)
        
        if output_type == "list":
            result = []
            for file, label in zip(auduo_files, labels):
                result.append({"file_path": file, "label": f"spk{label}"})
            return result

if __name__ == "__main__":
    
    audios_path = r"E:\AIDB\小甜饼\filtered"
    speaker_classifier = SpeakerClassifier()
    print(speaker_classifier.generate(audios_path, min_num_spks=2))
