import gradio as gr

import sys
sys.path.append('.')

from src.list_merger.list_utils import merge_list_folders
from tools.i18n.i18n import I18nAuto
import os

i18n = I18nAuto(language=None, locale_path=os.path.join(os.path.dirname(__file__), "i18n/locale"))

port = 8995
is_share = True
if len(sys.argv) > 2:
    port = int(sys.argv[1])
    is_share = eval(sys.argv[2])

def get_relative_path(path, base):
    return os.path.relpath(path, base)

def save_srt_to_file(srt_text, save_folder, character):
    character_folder = os.path.join(save_folder, character)
    os.makedirs(character_folder, exist_ok=True)
    srt_file = os.path.join(character_folder, "merged.srt")
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write(srt_text)

def scan_list_folders(folder):
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    list_folders = []
    for list_folder in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, list_folder)):
            list_folders.append(get_relative_path(os.path.join(folder, list_folder), folder))
    first_list_folder = ""
    second_list_folder = ""
    if len(list_folders) > 0:
        first_list_folder = second_list_folder = list_folders[0]
    if len(list_folders) > 1:
        second_list_folder = list_folders[1]
    return gr.Dropdown(list_folders, value=first_list_folder), gr.Dropdown(list_folders, value=second_list_folder)

def preview_merged_list(first_list_folder, second_list_folder, merge_list_character_name, save_folder):
    if first_list_folder == "" or second_list_folder == "":
        return ""
    if first_list_folder == second_list_folder:
        gr.Warning(i18n("两个文件夹不能相同！！！"))
        return ""
    first_list_folder = os.path.join(save_folder, first_list_folder)
    second_list_folder = os.path.join(save_folder, second_list_folder)
    print(f"first_list_folder: {first_list_folder}, second_list_folder: {second_list_folder}")
    first_list = os.path.join(first_list_folder, [file for file in os.listdir(first_list_folder) if file.lower().endswith(".list")][0])
    second_list = os.path.join(second_list_folder, [file for file in os.listdir(second_list_folder) if file.lower().endswith(".list")][0])
    try:
        return merge_list_folders(first_list, second_list, merge_list_character_name, first_list_folder, second_list_folder)
    except Exception as e:
        gr.Warning(f"Can't Merge, Error: {e}")
        return ""


def run_as_Tab(app:gr.Blocks = None):
    
    with gr.Row():
        with gr.Column(scale=2):
            scan_list_folder = gr.Textbox("Output/sliced_audio", label=i18n("文件夹路径"),interactive=True)
            scan_list_button = gr.Button(i18n("扫描文件夹"), variant="secondary")
            first_list_folder = gr.Dropdown([], label=i18n("主文件夹"),interactive=True)
            second_list_folder = gr.Dropdown([], label=i18n("次文件夹"),interactive=True)
            merge_list_character_name = gr.Textbox("", label=i18n("角色名称，留空使用各自的"),interactive=True)
            merge_list_button = gr.Button(i18n("合并文件夹与List"), variant="primary")
        with gr.Column(scale=2):
            list_preview = gr.Textbox("", lines=20, max_lines=30, label=i18n("合并后的List"))

    scan_list_button.click(scan_list_folders, [scan_list_folder], [first_list_folder, second_list_folder])
    merge_list_button.click(preview_merged_list, [first_list_folder, second_list_folder, merge_list_character_name, scan_list_folder], [list_preview])

        

# 如果以模块形式运行
if __name__ == "__main__":
    with gr.Blocks() as app:
        with gr.Row():
            gr.HTML(f"""<h1>{i18n("List合并插件")}</h1>
            <p>{i18n("这是一个插件，用于合并List文件夹。")}</p><p>{i18n("作者: ")}<a href="https://github.com/X-T-E-R">XTer</a></p>
            """)
        run_as_Tab(app)
    app.launch(
        server_name="0.0.0.0",
        inbrowser=True,
        share=is_share,
        server_port=port,
        quiet=True,
    )
