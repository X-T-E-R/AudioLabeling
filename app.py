import importlib, os
import gradio as gr
from tools.i18n.i18n import I18nAuto

i18n = I18nAuto(language=None, locale_path=os.path.join(os.path.dirname(__file__), "i18n/locale"))
# 给定的模块列表
modules = [
    {"name": i18n("预处理音频"), "path": "srt_1.webui"},
    {"name": i18n("从srt和音频打标"), "path": "srt_slicer.webui"},
    {"name": i18n("合并list文件"), "path": "list_merger.webui"}
    
]


with gr.Blocks() as app:
    with gr.Row():
        gr.HTML(
            f"""<h1>{i18n("AudioLabeling")}</h1>
            <p>{i18n("这是一个程序，用于打标音频。")}</p><p>{i18n("作者: ")}<a href="https://github.com/X-T-E-R">XTer</a></p>"""
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
                        module.run_as_Tab()
                    except Exception as e:
                        gr.HTML(f"<h1>{i18n('加载模块失败')}</h1><p>{str(e)}</p>")

app.launch()
