import gradio as gr
from awk_plus_plus.interpreter.interpreter import evaluate, serializer

theme = gr.themes.Base(font=["DM Sans", 'ui-sans-serif', 'system-ui', '-apple-system'])

css = """
footer{display:none !important}
.dark  {
    --body-background-fill: rgb(18, 18, 18);
}
.gradio-container {
  border: none !important;
}
"""

def predict(expression):
    result = evaluate(expression, "db.sql")
    return result

with gr.Blocks(theme=theme, title="awk_plus_plus", css=css, analytics_enabled=False) as demo:
    gr.Markdown("# Greetings from awk_plus_plus!")
    expression = gr.Code(label="Expression", language="json")
    submit_btn = gr.Button("Interpret")
    result = gr.JSON()
    submit_btn.click(fn=predict, inputs=expression, outputs=result, api_name="interpret")



    demo.queue(default_concurrency_limit=40)
