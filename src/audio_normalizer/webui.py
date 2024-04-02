import gradio as gr

import sys
sys.path.append('.')

from src.audio_normalizer.my_utils import normalize_loudness
from tools.i18n.i18n import I18nAuto
from tools.my_utils import scan_audios_walk, scan_audios_and_folders
import os

i18n = I18nAuto(language=None, locale_path=os.path.join(os.path.dirname(__file__), "i18n/locale"))

port = 8996
is_share = True
if len(sys.argv) > 2:
    port = int(sys.argv[1])
    is_share = eval(sys.argv[2])


def get_audios_dropdown(folder):
    audio_list = scan_audios_and_folders(folder)
    if len(audio_list) == 0:
        return gr.Dropdown(value=None, choices=[""])
    else:
        return gr.Dropdown(value=audio_list[0], choices=audio_list)

def normalize_fn(audio_path, target_path, target_loudness, audio_files_dropdown, progress=gr.Progress()):
    gr.Info(i18n("开始归一化"))
    if os.path.isdir(audio_path):
        audio_list = [filename for filename in scan_audios_walk(audio_path)]
        if target_path == "":
            target_path = audio_path
        else:
            target_path = os.path.join(target_path, audio_files_dropdown)
        try:
            for audio in progress.tqdm(audio_list):
                normalize_loudness(os.path.join(audio_path, audio), target_loudness, os.path.join(target_path, audio))
            gr.Info(i18n("归一化完成！"))      
            return gr.Textbox(i18n("归一化完成！"))
        except Exception as e:
            gr.Warning(i18n("响度归一化过程中出错")+f": {e}")
    else:
        if target_path == "":
            target_path = audio_path
        else:
            audio_filename = os.path.basename(audio_path)
            target_path = os.path.join(target_path, audio_filename)
        try:
            normalize_loudness(audio_path, target_loudness, target_path)
            gr.Info(i18n("归一化完成！"))
            return gr.Textbox(i18n("归一化完成！"))
        except Exception as e:
            gr.Warning(i18n("响度归一化过程中出错")+f": {e}")


def change_rewrite_checkbox(rewrite_checkbox):
    if rewrite_checkbox:
        return gr.Textbox("", visible=False)
    else:
        return gr.Textbox("Output/normalized_audios", visible=True)


def print_filenames(audio_path):
    audio_list = []
    if os.path.isdir(audio_path):
        audio_list = [os.path.join(audio_path,filename) for filename in scan_audios_walk(audio_path)]
    else:
        audio_list = [audio_path]
    
    return "\n".join(audio_list)

def run_as_Tab(app:gr.Blocks = None):
    with gr.Row():
        gr.Markdown(f"""{i18n("用于将响度归一化到一个统一的值，可提供文件或文件夹。")}\n\n{i18n("对切分好的音频效果更佳。")}""")
    with gr.Row():
        with gr.Column(scale=2) as input_col:
            with gr.Tabs():
                with gr.Tab(i18n("读取本地文件")):
                    with gr.Group():
                        input_folder_path_text = gr.Textbox("Output/sliced_audio", label=i18n("文件夹路径"),interactive=True)
                        scan_folder_button = gr.Button(i18n("扫描文件夹"), variant="secondary",interactive=True)
                    audio_files_dropdown = gr.Dropdown([], label=i18n("音频文件/文件夹"),interactive=True)
                    scan_folder_button.click(get_audios_dropdown, [input_folder_path_text], outputs=[audio_files_dropdown])
                with gr.Tab(i18n("上传文件")):
                    upload_audio = gr.Audio(type="filepath",label=i18n("音频文件"))
                    # input_audio_file = gr.File(label=i18n("上传音频文件"), type="audio", file_types=["mp3", "wav", "ogg"])
            with gr.Tabs():
                with gr.Tab(i18n("内容预览")):
                    input_audio_path_text = gr.Textbox("" ,interactive=False, max_lines=10, lines=10 ,visible=False)
                    audio_files_preview_text = gr.Textbox("", label=i18n("音频文件"),interactive=False, max_lines=10, lines=10 ,visible=True)
            upload_audio.change(
                lambda x: gr.Textbox(x, lines=1),
                [upload_audio],
                outputs=[input_audio_path_text],
            ).then(
                lambda x: gr.Textbox(x, lines=1),
                [upload_audio],
                outputs=[audio_files_preview_text],
            )
            audio_files_dropdown.change(
                lambda folder, filename: gr.Textbox(
                    os.path.join(folder, filename)
                ),
                inputs=[input_folder_path_text, audio_files_dropdown],
                outputs=[input_audio_path_text],
            ).then(
                lambda folder, filename: gr.Textbox(
                    print_filenames(os.path.join(folder, filename))
                ),
                inputs=[input_folder_path_text, audio_files_dropdown],
                outputs=[audio_files_preview_text],
            )

        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.Tab(i18n("面板")):
                    with gr.Group():
                        rewrite_checkbox = gr.Checkbox(value=True, label=i18n("覆盖原文件"),interactive=True)
                        target_path_text = gr.Textbox("Output/normalized_audios", label=i18n("目标文件夹"),interactive=True)
                        target_loudness = gr.Slider(-40, 0, -16, step=0.1, label=i18n("目标响度（LUFS）"),interactive=True)
                    with gr.Group():
                        status_text = gr.Textbox("", label=i18n("状态"),interactive=False, lines=1)
                        normalize_button = gr.Button(i18n("统一响度"), variant="primary",interactive=True)
        rewrite_checkbox.change(change_rewrite_checkbox, [rewrite_checkbox], outputs=[target_path_text])
        normalize_button.click(
            lambda x: gr.Textbox(i18n("开始归一化")), [], [status_text]
        ).then(
            normalize_fn,
            [
                input_audio_path_text,
                target_path_text,
                target_loudness,
                audio_files_dropdown,
            ],
            [status_text],
        )

# 如果以模块形式运行
if __name__ == "__main__":
    with gr.Blocks() as app:
        with gr.Row():
            gr.HTML(f"""<h1>{i18n("响度标准化")}</h1>""")
        run_as_Tab()
        
    app.launch(
        server_name="0.0.0.0",
        inbrowser=True,
        share=is_share,
        server_port=port,
        quiet=True,
    )
