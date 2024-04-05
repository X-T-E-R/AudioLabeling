import gradio as gr

import sys
sys.path.append('.')

from typing import List
from tools.i18n.i18n import I18nAuto
from tools.my_utils import scan_audios_walk, scan_audios_and_folders, scan_ext
import os, json

i18n = I18nAuto(language=None, locale_path=os.path.join(os.path.dirname(__file__), "i18n/locale"))

port = 8993
is_share = False
if len(sys.argv) > 2:
    port = int(sys.argv[1])
    is_share = eval(sys.argv[2])

try:
    from src.emotion_recognition.audio2emotion import Audio2Emotion
    model_available = True
except Exception as e:
    model_available = False

global audio2emotion
audio2emotion = None

def get_audios_dropdown(folder):
    audio_list = scan_audios_and_folders(folder)
    if len(audio_list) == 0:
        return gr.Dropdown(value=None, choices=[""])
    else:
        return gr.Dropdown(value=audio_list[0], choices=audio_list)

def print_filenames(audio_path):
    audio_list = []
    if os.path.isdir(audio_path):
        audio_list = [os.path.join(audio_path,filename) for filename in scan_audios_walk(audio_path)]
    else:
        audio_list = [audio_path]
    
    return "\n".join(audio_list)

def load_from_model_status():
    global audio2emotion
    if audio2emotion is None:
        return [
            gr.Textbox(interactive=True, visible=True),
            gr.Checkbox(interactive=True, visible=False),
            gr.Textbox("未加载模型", interactive=False),
            gr.Button(interactive=True, visible=True),
            gr.Button(interactive=False, visible=False)
            ]
    else:
        return [
            gr.Textbox(interactive=False, visible=False),
            gr.Checkbox(interactive=False, visible=False),
            gr.Textbox("已加载模型", interactive=False),
            gr.Button(interactive=False, visible=False),
            gr.Button(interactive=True, visible=True)
            ]

def load_model(models_path, use_cam):
    global audio2emotion
    if not model_available:
        gr.Warning(i18n("请先安装funasr模块，并检查是否安装torch。"))
        return load_from_model_status()
    if audio2emotion is None:
        gr.Info(i18n("开始加载模型，如果您并未使用手动提供模型并且第一次使用，请耐心等待modelscope下载有关模型。"))
        audio2emotion = Audio2Emotion(models_path)
        gr.Info(i18n("模型加载成功！"))
    else:
        gr.Info(i18n("请勿重复加载，刷新页面以获得最新情况！"))
    return load_from_model_status()

def unload_model():
    global audio2emotion
    if audio2emotion is not None:
        audio2emotion = None
        gr.Info(i18n("模型卸载成功！"))
    return load_from_model_status()

def generate_json_fn(audio_path, save_vec = False, return_list=False, progress = gr.Progress()):
    global audio2emotion
    if audio2emotion is None:
        if not model_available:
            gr.Warning(i18n("请先安装funasr模块，并检查是否安装torch。"))
        else:
            gr.Warning(i18n("请先加载模型！"))
        return ""
    else:
        assert isinstance(audio2emotion, Audio2Emotion)
        audio_list: List[str] = []
        save_json_path = ""
        if os.path.isdir(audio_path):
            audio_list = [filename for filename in scan_audios_walk(audio_path)]
            save_json_path = os.path.join(audio_path, "emotion_recognition.json")
        else:
            audio_list = [audio_path]
            save_json_path = audio_path.rsplit(".", 1)[0] + ".json"
        gr.Info(f"{i18n('开始生成emotion')}")
        recognized_emotions = []
        for audio_file in progress.tqdm(audio_list):
            audio_file_full_path = os.path.join(audio_path, audio_file) if audio_file!=audio_path else audio_path
            print(audio_file_full_path)
            result = {}
            try:
                if save_vec:
                    emotion, emotion_vec = audio2emotion.get_emotion(audio_path=audio_file_full_path, return_vec=True)
                    result["emotion_vec"] = emotion_vec
                else:
                    emotion = audio2emotion.get_emotion(audio_path=audio_file_full_path)
                result["audio_path"] = audio_file
                result["emotion"] = emotion
            except Exception as e:
                gr.Warning(f"{i18n('生成emotion失败！')} {e}")
            recognized_emotions.append(result)
        json_content = json.dumps(recognized_emotions, ensure_ascii=False, indent=4)
        try:
            with open(save_json_path, "w", encoding="utf-8") as f:
                f.write(json_content)
        except Exception as e:
            gr.Warning(f"{i18n('保存json文件失败！')} {e}")
    if return_list:
        return json_content, recognized_emotions
    else:
        return gr.Textbox(json_content)

def generate_emotion_and_rename_fn(audio_path, save_vec = False, update_list = False, progress = gr.Progress()):
    json_content, recognized_emotions = generate_json_fn(audio_path, save_vec, return_list=True, progress=progress)
    if update_list:
        list_file = scan_ext(audio_path, ["list"])
        if len(list_file) > 0:
            with open(os.path.join(audio_path, list_file[0]), "r", encoding="utf-8") as f:
                list_content = f.read()
        else:
            update_list = False
    for result in recognized_emotions:
        audio_file = result["audio_path"]
        audio_file_full_path = os.path.join(audio_path, audio_file) if audio_file!=audio_path else audio_path
        base_name = os.path.basename(audio_file)
        audio_dir = os.path.dirname(audio_file_full_path)
        emotion = result["emotion"]
        if len(emotion.split("/")) > 1:
            emotion = emotion.split("/")[0]
        new_name = f"{emotion}#{base_name}"
        try:
            os.rename(audio_file_full_path, os.path.join(audio_dir, new_name))
        except Exception as e:
            gr.Warning(f"{i18n('重命名文件失败！')} {e}")
        if update_list:
            list_content = list_content.replace(base_name, new_name)
    if update_list:
        with open(os.path.join(audio_path, list_file[0]), "w", encoding="utf-8") as f:
            f.write(list_content)
    return gr.Textbox(json_content)

def run_as_Tab(app:gr.Blocks = None):
    with gr.Row():
        gr.Markdown(i18n("本页面基于 emotion2vec （使用funasr） 作为核心，可以识别音频为9种典型情绪。")+"\n\n"+ i18n("如果您想使用cuda，需要按照readme安装对应版本的torch")+ "\n\n"+ i18n("您可以自动下载或手动放置模型文件，具体操作见readme。"))
    with gr.Row():
        with gr.Column(scale=2) as input_col:
            with gr.Tabs():
                with gr.Tab(i18n("读取本地文件")):
                    with gr.Group():
                        input_folder_path_text = gr.Textbox("Input/srt_and_audios", label=i18n("文件夹路径"),interactive=True)
                        scan_folder_button = gr.Button(i18n("扫描文件夹"), variant="secondary",interactive=True)
                    audio_files_dropdown = gr.Dropdown([], label=i18n("音频文件/文件夹"),interactive=True)
                    
                with gr.Tab(i18n("上传文件")):
                    upload_audio = gr.Audio(type="filepath",label=i18n("音频文件"))
            with gr.Tabs():
                with gr.Tab(i18n("内容预览")):
                    input_audio_path_text = gr.Textbox("", label=i18n("音频文件/文件夹"),interactive=False, visible=False)
                    audio_files_preview_text = gr.Textbox("", label=i18n("音频文件"),interactive=False, max_lines=10, lines=10 ,visible=True)
            scan_folder_button.click(
                get_audios_dropdown,
                [input_folder_path_text],
                outputs=[audio_files_dropdown],
            ).then(
                lambda folder, filename: gr.Textbox(os.path.join(folder, filename)),
                inputs=[input_folder_path_text, audio_files_dropdown],
                outputs=[input_audio_path_text],
            )
            upload_audio.change(
                lambda x: gr.Textbox(x), [upload_audio], outputs=[input_audio_path_text]
            ).then(
                lambda x: gr.Textbox(x),
                [upload_audio],
                outputs=[audio_files_preview_text],
            )
            audio_files_dropdown.input(
                lambda folder, filename: gr.Textbox(os.path.join(folder, filename)),
                inputs=[input_folder_path_text, audio_files_dropdown],
                outputs=[input_audio_path_text],
            )
            input_audio_path_text.change(
                lambda x: gr.Textbox(print_filenames(x)),
                inputs=[input_audio_path_text],
                outputs=[audio_files_preview_text],
            )

        with gr.Column(scale=1):
            with gr.Tabs():
                with gr.Tab(i18n("操作面板")):
                    with gr.Group():
                        models_path_text = gr.Textbox("models", label=i18n("模型文件夹路径（留空或不存在会自动下载）"),interactive=True)
                        use_cam_checkbox = gr.Checkbox(label=i18n("进行多说话人分类"), interactive=True, visible=False)
                        model_status_text = gr.Textbox("", label=i18n("模型状态"),interactive=False)
                        load_model_button = gr.Button(i18n("加载模型"), interactive=True, visible=True, variant="primary")
                        unload_model_button = gr.Button(i18n("卸载模型"), interactive=True, visible=False, variant="secondary")
                    with gr.Group():
                        save_vec_checkbox = gr.Checkbox(label=i18n("同时保存识别结果向量"), interactive=True)
                        generate_emotion_json_button = gr.Button(i18n("识别感情成json"), variant="primary",interactive=True)
                    with gr.Group():
                        update_list_checkbox = gr.Checkbox(value=True, label=i18n("同时更新list文件中的文件名"), interactive=True)
                        generate_emotion_and_rename_button = gr.Button(i18n("识别感情并重命名"), variant="primary",interactive=True)
                    app.load(
                        load_from_model_status,
                        [],
                        [
                            models_path_text,
                            use_cam_checkbox,
                            model_status_text,
                            load_model_button,
                            unload_model_button,
                        ],
                    )
                    load_model_button.click(
                        lambda x: [gr.update(interactive=False),gr.update(interactive=False)], [], [generate_emotion_json_button,load_model_button]
                    ).then(
                        load_model,
                        [models_path_text, use_cam_checkbox],
                        [
                            models_path_text,
                            use_cam_checkbox,
                            model_status_text,
                            load_model_button,
                            unload_model_button,
                        ],
                    ).then(
                        lambda x: gr.update(interactive=True), [], [generate_emotion_json_button]
                    )

        with gr.Column(scale=2):
            output_text = gr.Textbox("", label=i18n("输出"),interactive=False, lines=10, max_lines=20)
        unload_model_button.click(
            unload_model,
            [],
            [
                models_path_text,
                use_cam_checkbox,
                model_status_text,
                load_model_button,
                unload_model_button,
            ],
        )
        generate_emotion_json_button.click(
            lambda x: [gr.update(interactive=False), gr.update(interactive=False)], [], [generate_emotion_json_button, generate_emotion_and_rename_button]
        ).then(
            generate_json_fn,
            [input_audio_path_text, save_vec_checkbox],
            [output_text]
        ).then(
            lambda x: [gr.update(interactive=True),gr.update(interactive=True)] , [], [generate_emotion_json_button, generate_emotion_and_rename_button]
        )
        generate_emotion_and_rename_button.click(
            lambda x: [gr.update(interactive=False), gr.update(interactive=False)], [], [generate_emotion_json_button, generate_emotion_and_rename_button]
        ).then(
            generate_emotion_and_rename_fn,
            [input_audio_path_text, save_vec_checkbox, update_list_checkbox],
            [output_text]
        ).then(
            lambda x: [gr.update(interactive=True),gr.update(interactive=True)] , [], [generate_emotion_json_button, generate_emotion_and_rename_button]
        )       


# 如果以模块形式运行
if __name__ == "__main__":
    with gr.Blocks() as app:
        with gr.Row():
            gr.HTML(f"""<h1>{i18n("空白模板示例")}</h1>
            <p>{i18n("这是一个空白模板示例。")}</p>
            """)
        
        run_as_Tab(app=app)
        
    app.launch(
        server_name="0.0.0.0",
        inbrowser=True,
        share=is_share,
        server_port=port,
        quiet=True,
    )
