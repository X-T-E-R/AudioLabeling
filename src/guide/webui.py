import gradio as gr

import sys
sys.path.append('.')

from tools.i18n.i18n import I18nAuto
import os

i18n = I18nAuto(language=None, locale_path=os.path.join(os.path.dirname(__file__), "i18n/locale"))

port = 8989
is_share = True
if len(sys.argv) > 2:
    port = int(sys.argv[1])
    is_share = eval(sys.argv[2])


markdown_file = os.path.join("guide_cn.md")
with open(markdown_file, "r", encoding="utf-8") as f:
    markdown_text = f.read()

def run_as_Tab(app:gr.Blocks = None):
    
    with gr.Row():
        gr.Markdown(markdown_text)

# 如果以模块形式运行
if __name__ == "__main__":
    with gr.Blocks() as app:
        with gr.Row():
            gr.HTML(f"""<h1>{i18n("Guide")}</h1>
            """)
        run_as_Tab()
        
    app.launch(
        server_name="0.0.0.0",
        inbrowser=True,
        share=is_share,
        server_port=port,
        quiet=True,
    )
