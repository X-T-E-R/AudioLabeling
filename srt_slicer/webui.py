import gradio as gr

import sys
sys.path.append('.')

from srt_slicer.srt_utils import merge_subtitles_with_lib, parse_srt_with_lib, generate_srt_with_lib, slice_audio_with_lib, count_words_multilang
from tools.i18n.i18n import I18nAuto
import os

i18n = I18nAuto(language=None, locale_path=os.path.join(os.path.dirname(__file__), "i18n/locale"))

port = 8991
is_share = True
if len(sys.argv) > 2:
    port = int(sys.argv[1])
    is_share = eval(sys.argv[2])
 

def merge_srt(input_text, output_text, short_interval=0.1, max_interval=1, max_text_length=30, add_period=True, merge_zero_interval=True):
    original_subtitles = parse_srt_with_lib(input_text)
    merged_subtitles = merge_subtitles_with_lib(original_subtitles, short_interval, max_interval, max_text_length, add_period, merge_zero_interval)
    output_text = generate_srt_with_lib(merged_subtitles)
    return output_text


def slice_audio(
    input_audio,
    save_folder,
    audio_format,
    output_text,
    pre_preserve_time,
    post_preserve_time,
    pre_silence_time,
    post_silence_time,
    language,
    character,
    
):
    if isinstance(input_audio, str) and input_audio != "":
        pass
    else:
        gr.Warning(i18n("找不到音频！！！"))
        return
    if output_text == "":
        gr.Warning(i18n("找不到字幕！！！"))
        return
    
    character_folder = os.path.join(save_folder, character)
    os.makedirs(character_folder, exist_ok=True)
    subtitles = parse_srt_with_lib(output_text)
    try:
        gr.Info(f"{i18n('正在切分音频')} {input_audio} {i18n('到')} {character_folder}")
        slice_audio_with_lib(
            input_audio,
            character_folder,
            audio_format,
            subtitles,
            pre_preserve_time,
            post_preserve_time,
            pre_silence_time,
            post_silence_time,
            language,
            character,
        )
        gr.Info(f"{i18n('切分完成')} ")
    except Exception as e:
        gr.Warning(f"Can't Slice, Error: {e}")

def get_relative_path(path, base):
    return os.path.relpath(path, base)

def get_srt_and_audio_files(folder):
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    srt_files = []
    audio_files = []            
    audio_file_formats = ["mp3", "wav", "ogg", "flac"]
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".srt"):
                srt_files.append(get_relative_path(os.path.join(root, file), folder))
            for audio_file_format in audio_file_formats:
                if file.lower().endswith(audio_file_format):
                    audio_files.append(get_relative_path(os.path.join(root, file), folder))
    srt_file = ""
    audio_file = ""
    if len(srt_files) > 0:
        srt_file = srt_files[0]
    if len(audio_files) > 0:
        audio_file = audio_files[0]
    return gr.Dropdown(srt_files,value=srt_file), gr.Dropdown(audio_files,value=audio_file)

def change_srt_file(folder,srt_file):
    srt_folder = os.path.dirname(os.path.join(folder, srt_file))
    basename = os.path.basename(srt_file).rsplit(".", 1)[0]
    audio_file_formats = ["mp3", "wav", "ogg", "flac"]
    for file in os.listdir(srt_folder):
        print(f"basename: {basename}, file: {file}")
        if basename.lower() in file.lower():
            for audio_file_format in audio_file_formats:
                if file.lower().endswith(audio_file_format):
                    return gr.Dropdown(value=get_relative_path(os.path.join(srt_folder, file), folder))
    return gr.Dropdown(interactive=True)

def filter_srt(input_text, min_length, filter_english, filter_words):
    subtitles = parse_srt_with_lib(input_text)
    filtered_subtitles = []
    for subtitle in subtitles:
        if count_words_multilang(subtitle.content) >= min_length:
            flag = False
            if filter_english:
                for i in subtitle.content:
                    if i in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        flag = True
                        break
            if not flag and filter_words:
                filter_words.replace("\r", "\n")
                for word in filter_words.split("\n"):
                    if word in subtitle.content:
                        flag = True
                        break
            if not flag:
                filtered_subtitles.append(subtitle)
    return generate_srt_with_lib(filtered_subtitles)

def load_srt_from_file(srt_file):
    try:
        with open(srt_file, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def load_audio_from_file(audio_file):
    try:
        return gr.Audio(audio_file)
    except:
        return gr.Audio(value=None)

def load_from_dropdown(input_folder, srt_files_list, audio_files_list):
    if isinstance(srt_files_list, str) and isinstance(audio_files_list, str):
        srt_file= os.path.join(input_folder, srt_files_list)
        audio_file = os.path.join(input_folder, audio_files_list)
        return load_srt_from_file(srt_file), load_audio_from_file(audio_file)
    else:
        return "", gr.Audio(value=None)

def enable_gr_elements(*args):
    return [gr.update(interactive=True) for _ in args]

def disable_gr_elements(*args):
    return [gr.update(interactive=False) for _ in args]

def save_srt_to_file(srt_text, save_folder, character):
    character_folder = os.path.join(save_folder, character)
    os.makedirs(character_folder, exist_ok=True)
    srt_file = os.path.join(character_folder, "merged.srt")
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write(srt_text)
        
from datetime import datetime

def change_character_name(input_audio):
    try:
        input_audio_name = os.path.basename(input_audio).rsplit(".", 1)[0]
        character = input_audio_name[:20]
    except:
        character = datetime.now().strftime("%m%d%H%M")
    return gr.Textbox(value=character)

def check_character_foldfer(folder, character):
    character_folder = os.path.join(folder, character)
    if os.path.exists(character_folder):
        return gr.Textbox(visible=True)
    return gr.Textbox(visible=False)

def run_as_Tab():
     with gr.Row():
        with gr.Column(scale=2) as input_col:
            with gr.Tabs():
                with gr.Tab(i18n("读取本地文件")):
                    input_folder = gr.Textbox("input/srt_and_audios", label=i18n("文件夹路径"),interactive=True)
                    scan_button = gr.Button(i18n("扫描文件夹"), variant="secondary",interactive=True)
                    srt_files_list = gr.Dropdown([], label=i18n("SRT文件"),interactive=True)
                    audio_files_list = gr.Dropdown([], label=i18n("音频文件"),interactive=True)
                    srt_read_button = gr.Button(i18n("读取文件"), variant="secondary",interactive=True)
                with gr.Tab(i18n("上传文件")):
                    input_srt_file = gr.File(label=i18n("上传SRT文件"), type="filepath", file_types=["srt"])
                    upload_audio = gr.Audio(type="filepath",label=i18n("音频文件"))
                    # input_audio_file = gr.File(label=i18n("上传音频文件"), type="audio", file_types=["mp3", "wav", "ogg"])
            with gr.Tabs():
                with gr.Tab(i18n("内容预览")):
                    input_audio = gr.Textbox("", label=i18n("音频文件"),interactive=False)
                    input_text = gr.Textbox("", lines=20, max_lines=30, label=i18n("srt文件内容"))
            input_srt_file.change(load_srt_from_file, [input_srt_file], [input_text])
        with gr.Column(scale=1) as control_col:
            with gr.Tabs():
                with gr.Tab(i18n("合并字幕设置")):
                    merge_zero_interval = gr.Checkbox(label=i18n("提前合并时间间隔很短的字幕"),interactive=True, value=True)
                    short_interval = gr.Slider(value=0.05, minimum=0, maximum=0.5, step=0.005, label=i18n("判定为短间隔时长"),interactive=True,visible=True)
                    max_interval = gr.Slider(value=0.8, minimum=0.1, maximum=10, step=0.1, label=i18n("最大间隔时间"),interactive=True)
                    max_text_length = gr.Slider(value=50,minimum=5,maximum=200,step=1, label=i18n("最长允许单句长度"),interactive=True)
                    add_period = gr.Checkbox(label=i18n("句末加句号"),interactive=True, value=True)
                    merge_button = gr.Button(i18n("合并字幕"), variant="primary")

                with gr.Tab(i18n("过滤设置")):
                    min_length = gr.Slider(value=5, minimum=0, maximum=20, step=1, label=i18n("允许最短长度"),interactive=True)
                    filter_english = gr.Checkbox(label=i18n("过滤带有英文的"),interactive=True)
                    filter_words = gr.Textbox("", label=i18n("过滤词语，一行一个"),lines=5,max_lines=10,interactive=True)
                    filter_button = gr.Button(i18n("过滤字幕"), variant="primary",interactive=False)
                with gr.Tab(i18n("切分与保存")):
                    with gr.Group():
                        pre_preserve_time = gr.Slider(value=0.1, minimum=0, maximum=1, step=0.01, label=i18n("前置保留时间"),interactive=True)
                        post_preserve_time = gr.Slider(value=0.1, minimum=0, maximum=1, step=0.01, label=i18n("后置保留时间"),interactive=True)
                        pre_silence_time = gr.Slider(value=0.05, minimum=0, maximum=1, step=0.01, label=i18n("前置添加静音时间"),interactive=True,visible=False)
                        post_silence_time = gr.Slider(value=0.1, minimum=0, maximum=1, step=0.01, label=i18n("后置添加静音时间"),interactive=True,visible=False)
                    with gr.Group():
                        language = gr.Dropdown([i18n(i) for i in [ "ZH", "EN", "JA"]], value="ZH", label=i18n("语言"),interactive=True)
                        audio_format = gr.Dropdown(["mp3", "wav", "ogg"], value="wav", label=i18n("音频格式"),interactive=True)
                    with gr.Group():
                        save_folder = gr.Textbox("output/sliced_audio", label=i18n("保存文件夹"),interactive=True)
                        character = gr.Textbox("character", label=i18n("保存子文件夹名称"),interactive=True)
                        character_warning = gr.Textbox(i18n("注意：该文件夹已存在"), label=i18n("提示"),interactive=False,visible=False)
                    save_srt_button = gr.Button(i18n("保存合并后字幕"),variant="secondary",interactive=True)
                    slice_audio_button = gr.Button(i18n("切分并保存音频、list"), variant="primary",interactive=False)

        with gr.Column(scale=2) as output_col:
            with gr.Tabs():
                with gr.Tab(i18n("合并后srt文本")):
                    output_text = gr.Textbox("", lines=20, max_lines=30, label="Sliced SRT")
                with gr.Tab(i18n("切分预览")):
                    gr.Textbox(i18n("正在建设，敬请期待"), label=i18n("提示"),interactive=False)
        scan_button.click(get_srt_and_audio_files, [input_folder], [srt_files_list, audio_files_list])
        merge_zero_interval.change(lambda x: gr.update(visible=x), [merge_zero_interval],[short_interval])
        srt_files_list.change(change_srt_file, [input_folder, srt_files_list], [audio_files_list])
        srt_read_button.click(
            load_from_dropdown,
            [input_folder, srt_files_list, audio_files_list],
            [input_text, input_audio],
        )
        input_text.change(
            disable_gr_elements,
            [slice_audio_button, filter_button],
            [slice_audio_button, filter_button],
        ).then(
            change_character_name,
            [input_audio],
            [character],
        )

        upload_audio.change(
            change_character_name,
            [upload_audio],
            [character],
        ).then(
            lambda x:gr.Textbox(value=x),
            [upload_audio],
            [input_audio],
        )

        merge_button.click(
            merge_srt,
            [
                input_text,
                output_text,
                short_interval,
                max_interval,
                max_text_length,
                add_period,
                merge_zero_interval
            ],
            [output_text],
        ).then(
            enable_gr_elements,
            [slice_audio_button, filter_button],
            [slice_audio_button, filter_button],
        )
        slice_audio_button.click(
            slice_audio,
            [
                input_audio,
                save_folder,
                audio_format,
                output_text,
                pre_preserve_time,
                post_preserve_time,
                pre_silence_time,
                post_silence_time,
                language,
                character
            ],
           
        )
        save_srt_button.click(
            save_srt_to_file,
            [output_text, save_folder, character],
            
        )
        filter_button.click(
            filter_srt,
            [output_text, min_length, filter_english, filter_words],
            [output_text],
        )
        character.change(
            check_character_foldfer,
            [save_folder, character],
            [character_warning],
        )

# 如果以模块形式运行
if __name__ == "__main__":
    with gr.Blocks() as app:
        with gr.Row():
            gr.HTML(f"""<h1>{i18n("SRT合并切分插件")}</h1>
            <p>{i18n("这是一个插件，用于依靠SRT文件得到切分与打标好的音频。")}</p><p>{i18n("作者: ")}<a href="https://github.com/X-T-E-R">XTer</a></p>
            <h2>{i18n("使用方法")}</h2>
            <ol>
                <li>{i18n("提供SRT文件（可使用剪映或者ASR工具获得）与原始音频文件。")}</li>
                <li>{i18n("根据面板合并短句并过滤你不希望出现的句子。")}</li>
                <li>{i18n("随后保存成切分好的音频与list文件。")}</li>
            </ol>""")
        run_as_Tab()
    app.launch(
        server_name="0.0.0.0",
        inbrowser=True,
        share=is_share,
        server_port=port,
        quiet=True,
    )
