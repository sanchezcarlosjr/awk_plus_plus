import gradio as gr
from awk_plus_plus.interpreter.interpreter import evaluate, serializer
from kink import di

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
    exclusive_expression = di['exclusive_expression']
    if exclusive_expression is not None:
        return evaluate(exclusive_expression, "db.sql")
    return evaluate(expression, "db.sql")


with gr.Blocks(theme=theme, title="awk_plus_plus", css=css, analytics_enabled=False) as demo:
    gr.Markdown("# Greetings from Awk Plus Plus!")
    expression = gr.Code(label="Expression", language="json")
    submit_btn = gr.Button("Interpret")
    result = gr.JSON()
    submit_btn.click(fn=predict, inputs=expression, outputs=result, api_name="interpret")

