import importlib, os
import gradio as gr
from tools.i18n.i18n import I18nAuto

i18n = I18nAuto(language=None, locale_path=os.path.join(os.path.dirname(__file__), "i18n/locale"))
# 给定的模块列表
modules = [
    {"name": i18n("指南"), "path": "src.guide.webui"},
    {"name": i18n("生成srt"), "path": "src.srt_generator.webui"},
    {"name": i18n("从srt和音频切分"), "path": "src.srt_slicer.webui"},
    {"name": i18n("合并list文件"), "path": "src.list_merger.webui"},
    {"name": i18n("响度标准化"), "path": "src.audio_normalizer.webui"},
    {"name": i18n("情感识别"), "path": "src.emotion_recognition.webui"},
    {"name": i18n("多说话人分类(在做)"), "path": "src.speaker_classifier.webui"},
    {"name": i18n("音频降噪与增强(没做好)"), "path": "src.audio_enhancer.webui"},
    # {"name": i18n("list文件筛选器(没做好)"), "path": "src.list_filter.webui"},
    # {"name": i18n("从已有数据集生成list(没做好)"), "path": "src.list_generator.webui"},
    {"name": i18n("模板示例"), "path": "src.empty_template.webui"},
]


with gr.Blocks() as app:
    with gr.Row():
        gr.HTML(
            f"""<h1>{i18n("AudioLabeling")}</h1>
            <p>{i18n("这是一个程序，用于处理音频数据集")}</p><p>{i18n("开源地址: ")}<a href="https://github.com/X-T-E-R/AudioLabeling">github</a></p>"""
        )
    with gr.Row():
        # 选择要使用的模块
        with gr.Tabs():
            for module_info in modules:
                with gr.Tab(label=module_info["name"]):
                    # 动态导入模块
                    try:
                        module = importlib.import_module(module_info["path"])
                        # 调用模块中的函数
                        module.run_as_Tab(app)
                    except Exception as e:
                        gr.HTML(f"<h1>{i18n('加载模块失败')}</h1><p>{str(e)}</p>")

app.launch()
