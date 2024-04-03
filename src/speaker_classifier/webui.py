import gradio as gr

import sys
sys.path.append('.')

from typing import List
from tools.i18n.i18n import I18nAuto
from tools.my_utils import scan_audios_walk, scan_audios_and_folders
import os

i18n = I18nAuto(language=None, locale_path=os.path.join(os.path.dirname(__file__), "i18n/locale"))

port = 8993
is_share = False
if len(sys.argv) > 2:
    port = int(sys.argv[1])
    is_share = eval(sys.argv[2])

try:
    from src.srt_generator.audio2srt import Audio2Srt
    asr_available = True
except Exception as e:
    asr_available = False

global audio2srt
audio2srt = None

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
    global audio2srt
    if audio2srt is None:
        return [
            gr.Textbox(interactive=True, visible=True),
            gr.Checkbox(interactive=True, visible=True),
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
    global audio2srt
    if not asr_available:
        gr.Warning(i18n("请先安装funasr模块，并检查是否安装torch。"))
        return load_from_model_status()
    if audio2srt is None:
        gr.Info(i18n("开始加载模型，如果您并未使用手动提供模型并且第一次使用，请耐心等待modelscope下载有关模型。"))
        audio2srt = Audio2Srt(models_path, allow_spk=use_cam)
        gr.Info(i18n("模型加载成功！"))
    else:
        gr.Info(i18n("请勿重复加载，刷新页面以获得最新情况！"))
    return load_from_model_status()

def unload_model():
    global audio2srt
    if audio2srt is not None:
        audio2srt = None
        gr.Info(i18n("模型卸载成功！"))
    return load_from_model_status()

def generate_srt_fn(audio_path, progress = gr.Progress()):
    global audio2srt
    if audio2srt is None:
        if not asr_available:
            gr.Warning(i18n("请先安装funasr模块，并检查是否安装torch。"))
        else:
            gr.Warning(i18n("请先加载模型！"))
        return ""
    else:
        audio_list: List[str] = []
        if os.path.isdir(audio_path):
            audio_list = [os.path.join(audio_path,filename) for filename in scan_audios_walk(audio_path)]
        else:
            audio_list = [audio_path]
        gr.Info(f"{i18n('开始生成srt文件')}")
        target_filepaths = []
        for audio_file in progress.tqdm(audio_list):
            try:
                srt_content = audio2srt.generate_srt(audio_file)
            except Exception as e:
                gr.Warning(f"{i18n('生成srt文件失败！')} {e}")
            target_filepath = audio_file.rsplit(".", 1)[0] + ".srt"
            try:
                os.makedirs(os.path.dirname(target_filepath), exist_ok=True)
                with open(target_filepath, "w", encoding="utf-8") as f:
                    f.write(srt_content)
                    target_filepaths.append(target_filepath)
            except Exception as e:
                gr.Warning(f"{i18n('生成srt文件失败！')} {e}")
    return gr.Textbox("\n".join(target_filepaths))

def run_as_Tab(app:gr.Blocks = None):
    with gr.Row():
        gr.Markdown(i18n("本页面基于funasr作为语音转文字的核心， 您也可以使用 剪映 等软件用以生成字幕文件。")+"\n\n"+ i18n("需要大约3个G的显存/内存与torch，您需要按照readme安装对应版本的torch")+ "\n\n"+ i18n("您可以自动下载或手动放置ASR模型文件，具体操作见readme。"))
    with gr.Row():
        with gr.Column(scale=2) as input_col:
            with gr.Tabs():
                with gr.Tab(i18n("读取本地文件")):
                    with gr.Group():
                        input_folder_path_text = gr.Textbox("Input/srt_and_audios", label=i18n("文件夹路径"),interactive=True)
                        scan_folder_button = gr.Button(i18n("扫描文件夹"), variant="secondary",interactive=True)
                    audio_files_dropdown = gr.Dropdown([], label=i18n("音频文件/文件夹"),interactive=True)
                    scan_folder_button.click(get_audios_dropdown, [input_folder_path_text], outputs=[audio_files_dropdown])
                with gr.Tab(i18n("上传文件")):
                    upload_audio = gr.Audio(type="filepath",label=i18n("音频文件"))
            with gr.Tabs():
                with gr.Tab(i18n("内容预览")):
                    input_audio_path_text = gr.Textbox("", label=i18n("音频文件/文件夹"),interactive=False, visible=False)
                    audio_files_preview_text = gr.Textbox("", label=i18n("音频文件"),interactive=False, max_lines=10, lines=10 ,visible=True)
            upload_audio.change(lambda x: gr.Textbox(x), [upload_audio], outputs=[input_audio_path_text]).then(lambda x: gr.Textbox(x), [upload_audio], outputs=[audio_files_preview_text])
            audio_files_dropdown.change(
                lambda folder, filename: gr.Textbox(os.path.join(folder, filename)),
                inputs=[input_folder_path_text, audio_files_dropdown],
                outputs=[input_audio_path_text],
            ).then(
                lambda folder, filename: gr.Textbox(
                    print_filenames(os.path.join(folder, filename))
                ),
                inputs=[input_folder_path_text, audio_files_dropdown],
                outputs=[audio_files_preview_text],
            )

        with gr.Column(scale=1):
            with gr.Tabs():
                with gr.Tab(i18n("操作面板")):
                    with gr.Group():
                        models_path_text = gr.Textbox("models/iic", label=i18n("模型文件夹路径（留空或不存在会自动下载）"),interactive=True)
                        use_cam_checkbox = gr.Checkbox(label=i18n("进行多说话人分类"), interactive=True)
                        model_status_text = gr.Textbox("", label=i18n("模型状态"),interactive=False)
                        load_model_button = gr.Button(i18n("加载模型"), interactive=True, visible=True, variant="primary")
                        unload_model_button = gr.Button(i18n("卸载模型"), interactive=True, visible=False, variant="secondary")
                    with gr.Group():
                        generate_srt_button = gr.Button(i18n("生成srt文件"), variant="primary",interactive=True)
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
                        lambda x: [gr.update(interactive=False),gr.update(interactive=False)], [], [generate_srt_button,load_model_button]
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
                        lambda x: gr.update(interactive=True), [], [generate_srt_button]
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
        generate_srt_button.click(
            lambda x: gr.update(interactive=False), [], [generate_srt_button]
        ).then(
            generate_srt_fn,
            [input_audio_path_text],
            [output_text]
        ).then(
            lambda x: gr.update(interactive=True), [], [generate_srt_button]
        )


# 如果以模块形式运行
if __name__ == "__main__":
    with gr.Blocks() as app:
        with gr.Row():
            gr.HTML(f"""<h1>{i18n("空白模板示例")}</h1>
            <p>{i18n("这是一个空白模板示例。")}</p>
            """)
        
        run_as_Tab(app)
        
    app.launch(
        server_name="0.0.0.0",
        inbrowser=True,
        share=is_share,
        server_port=port,
        quiet=True,
    )
