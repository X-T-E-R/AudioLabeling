import gradio as gr

import sys
sys.path.append('.')

from typing import List
from tools.i18n.i18n import I18nAuto
from tools.my_utils import scan_audios_walk, scan_folders, scan_ext
import os, json
import shutil

i18n = I18nAuto(language=None, locale_path=os.path.join(os.path.dirname(__file__), "i18n/locale"))

port = 8993
is_share = False
if len(sys.argv) > 2:
    port = int(sys.argv[1])
    is_share = eval(sys.argv[2])

try:
    from src.speaker_classifier.speaker_classifier import SpeakerClassifier
    model_available = True
except Exception as e:
    model_available = False

global speaker_classifier
speaker_classifier = None

def get_audios_dropdown(folder):
    audio_list = scan_folders(folder, add_self=True)
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
    global speaker_classifier
    if speaker_classifier is None:
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
    global speaker_classifier
    if not model_available:
        gr.Warning(i18n("请先安装funasr模块，并检查是否安装torch。"))
        return load_from_model_status()
    if speaker_classifier is None:
        gr.Info(i18n("开始加载模型，如果您并未使用手动提供模型并且第一次使用，请耐心等待modelscope下载有关模型。"))
        speaker_classifier = SpeakerClassifier(models_path)
        gr.Info(i18n("模型加载成功！"))
    else:
        gr.Info(i18n("请勿重复加载，刷新页面以获得最新情况！"))
    return load_from_model_status()

def unload_model():
    global speaker_classifier
    if speaker_classifier is not None:
        speaker_classifier = None
        gr.Info(i18n("模型卸载成功！"))
    return load_from_model_status()

def generate_json_fn(audio_path, min_spk_num, max_spk_num, return_list=False):
    assert os.path.isdir(audio_path)
    global speaker_classifier
    if speaker_classifier is None:
        if not model_available:
            gr.Warning(i18n("请先安装funasr模块，并检查是否安装torch。"))
        else:
            gr.Warning(i18n("请先加载模型！"))
        return ""
    else:
        assert isinstance(speaker_classifier, SpeakerClassifier)
        save_json_path = os.path.join(audio_path, "speaker.json")
        try:
            result = speaker_classifier.generate(audio_path, min_num_spks=min_spk_num, max_num_spks=max_spk_num)
        except Exception as e:
            gr.Warning(f"{i18n('识别说话人失败！')} {e}")
            return ""
        json_content = json.dumps(result, ensure_ascii=False, indent=4)
        try:
            with open(save_json_path, "w", encoding="utf-8") as f:
                f.write(json_content)
        except Exception as e:
            gr.Warning(f"{i18n('保存json文件失败！')} {e}")
    if return_list:
        return json_content, result
    else:
        return gr.Textbox(json_content)

def get_list_line(audio_name: str, original_list: str):
    for item in original_list:
        if audio_name.lower() in item.lower():
            return item
    

def generate_and_move_fn(audio_path, min_spk_num, max_spk_num, update_list=False, progress=gr.Progress()):
    assert os.path.isdir(audio_path)
    json_content, result = generate_json_fn(audio_path, min_spk_num, max_spk_num, return_list=True)
    if update_list:
        list_file = scan_ext(audio_path, ["list"])
        if len(list_file) > 0:
            with open(os.path.join(audio_path, list_file[0]), "r", encoding="utf-8") as f:
                original_list = f.readlines()
        else:
            update_list = False
    audio_path = os.path.abspath(audio_path)
    while audio_path[-1] in ["/", "\\"]:
        audio_path = audio_path[:-1]
    save_folder = audio_path + "_classified"
    if os.path.exists(save_folder):
        gr.Info(i18n("删除已存在的分类文件夹"))
        shutil.rmtree(save_folder)
    for item in progress.tqdm(result):
        new_folder = os.path.join(save_folder, item["label"])
        os.makedirs(new_folder, exist_ok=True)
        file_name = os.path.basename(item["file_path"])
        if update_list:
            line = get_list_line(file_name, original_list)
            with open(os.path.join(new_folder, "datamapping.list"), "a", encoding="utf-8") as f:
                f.write(line)
        try:
            shutil.copy(os.path.join(audio_path,item["file_path"]), os.path.join(new_folder,item["file_path"]))
        except Exception as e:
            gr.Warning(f"{i18n('复制文件失败！')} {e}")
    return gr.Textbox(json_content)

def run_as_Tab(app:gr.Blocks = None):
    with gr.Row():
        gr.Markdown(i18n("本页面基于funasr/cam++/3d_speaker，可以基于embedding来识别说话人。")+"\n\n"+ i18n("但还是相对较原始，欢迎来贡献补充 1.更多的提取embedding的方法 2.结果可视化")+ "\n\n"+ i18n("另外推荐领航员未鸟的ColorSplitter"))
    with gr.Row():
        with gr.Column(scale=2) as input_col:
            with gr.Tabs():
                with gr.Tab(i18n("读取本地文件")):
                    with gr.Group():
                        input_folder_path_text = gr.Textbox("Input/srt_and_audios", label=i18n("文件夹路径"),interactive=True)
                        scan_folder_button = gr.Button(i18n("扫描文件夹"), variant="secondary",interactive=True)
                        audio_files_dropdown = gr.Dropdown([], label=i18n("音频文件夹"), interactive=True)
                with gr.Tab(i18n("上传文件"),interactive=False,visible=False):
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
                        models_path_text = gr.Textbox("models/iic", label=i18n("模型文件夹路径（留空或不存在会自动下载）"),interactive=True)
                        use_cam_checkbox = gr.Checkbox(label=i18n("进行多说话人分类"), interactive=True, visible=False)
                        model_status_text = gr.Textbox("", label=i18n("模型状态"),interactive=False)
                        load_model_button = gr.Button(i18n("加载模型"), interactive=True, visible=True, variant="primary")
                        unload_model_button = gr.Button(i18n("卸载模型"), interactive=True, visible=False, variant="secondary")
                    with gr.Group():
                        min_spk_num_slider = gr.Slider(1, 20, 1, step=1, label=i18n("最少说话人数"),interactive=True)
                        max_spk_num_slider = gr.Slider(1, 20, 10, step=1, label=i18n("最多说话人数"),interactive=True)
                        generate_json_button = gr.Button(i18n("识别说话人成json"), variant="primary",interactive=True)
                    with gr.Group():
                        update_list_checkbox = gr.Checkbox(value=True, label=i18n("同时生成新的list文件"), interactive=True)
                        generate_and_move_button = gr.Button(i18n("识别并复制文件到新的文件夹"), variant="primary",interactive=True)
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
                        lambda x: [gr.update(interactive=False),gr.update(interactive=False)], [], [generate_json_button,load_model_button]
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
                        lambda x: gr.update(interactive=True), [], [generate_json_button]
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
        generate_json_button.click(
            lambda x: [gr.update(interactive=False), gr.update(interactive=False)], [], [generate_json_button, generate_and_move_button]
        ).then(
            generate_json_fn,
            [input_audio_path_text, min_spk_num_slider, max_spk_num_slider],
            [output_text]
        ).then(
            lambda x: [gr.update(interactive=True),gr.update(interactive=True)] , [], [generate_json_button, generate_and_move_button]
        )
        generate_and_move_button.click(
            lambda x: [gr.update(interactive=False), gr.update(interactive=False)], [], [generate_json_button, generate_and_move_button]
        ).then(
            generate_and_move_fn,
            [input_audio_path_text, min_spk_num_slider, max_spk_num_slider, update_list_checkbox],
            [output_text]
        ).then(
            lambda x: [gr.update(interactive=True),gr.update(interactive=True)] , [], [generate_json_button, generate_and_move_button]
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
