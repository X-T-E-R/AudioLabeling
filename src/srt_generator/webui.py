import gradio as gr

import sys
sys.path.append('.')


from tools.i18n.i18n import I18nAuto
from tools.my_utils import scan_audios_walk, scan_audios_and_folders
import os

i18n = I18nAuto(language=None, locale_path=os.path.join(os.path.dirname(__file__), "i18n/locale"))

port = 8993
is_share = False
if len(sys.argv) > 2:
    port = int(sys.argv[1])
    is_share = eval(sys.argv[2])


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
        

def run_as_Tab():
    with gr.Row():
        gr.Markdown(i18n("这一块内容还没有做好，推荐项目 https://github.com/alibaba-damo-academy/FunClip 或者 剪映 用以生成字幕文件。"))
    with gr.Row():
        with gr.Column(scale=2) as input_col:
            with gr.Tabs():
                with gr.Tab(i18n("读取本地文件")):
                    with gr.Group():
                        input_folder_path_text = gr.Textbox("Input/audios", label=i18n("文件夹路径"),interactive=True)
                        scan_folder_button = gr.Button(i18n("扫描文件夹"), variant="secondary",interactive=True)
                    audio_files_dropdown = gr.Dropdown([], label=i18n("音频文件/文件夹"),interactive=True)
                    scan_folder_button.click(get_audios_dropdown, [input_folder_path_text], outputs=[audio_files_dropdown])
                with gr.Tab(i18n("上传文件")):
                    upload_audio = gr.Audio(type="filepath",label=i18n("音频文件"))
            with gr.Tabs():
                with gr.Tab(i18n("内容预览")):
                    input_audio_path_text = gr.Textbox("", label=i18n("音频文件/文件夹"),interactive=False)
            upload_audio.change(lambda x: gr.Textbox(x), [upload_audio], outputs=[input_audio_path_text])
            audio_files_dropdown.change(lambda folder,filename: gr.Textbox(os.path.join(folder,filename)), inputs=[input_folder_path_text, audio_files_dropdown], outputs=[input_audio_path_text])
        
        with gr.Column(scale=1):
            with gr.Tabs():
                with gr.Tab(i18n("Tab的作用是为了好看")):
                    with gr.Group():
                        gr.Checkbox(label=i18n("空白复选框"),interactive=True)
                        gr.Textbox("", label=i18n("空白文本框"),interactive=True)
                        gr.Slider(0, 100, 50, label=i18n("空白滑条"),interactive=True)
                        gr.Button(i18n("空白按钮"), variant="secondary",interactive=True)
                    get_filenames_button = gr.Button(i18n("打印音频文件名"), variant="primary",interactive=True)
        with gr.Column(scale=2):
            output_text = gr.Textbox("", label=i18n("输出"),interactive=False, lines=10, max_lines=20)
        
        

# 如果以模块形式运行
if __name__ == "__main__":
    with gr.Blocks() as app:
        with gr.Row():
            gr.HTML(f"""<h1>{i18n("空白模板示例")}</h1>
            <p>{i18n("这是一个空白模板示例。")}</p>
            """)
        
        run_as_Tab()
        
    app.launch(
        server_name="0.0.0.0",
        inbrowser=True,
        share=is_share,
        server_port=port,
        quiet=True,
    )
