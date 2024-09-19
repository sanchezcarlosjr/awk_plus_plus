import gradio as gr
from awk_plus_plus.interpreter.interpreter import evaluate, serializer
from kink import di
import pandas as pd

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


def predict_as_dataframe(expression):
    return pd.DataFrame.from_records(predict(expression))


with gr.Blocks(theme=theme, title="awk_plus_plus", css=css, analytics_enabled=False) as demo:
    gr.Markdown("# Greetings from Awk Plus Plus!")
    expression = gr.Code(label="Expression", language="json")
    gr.Examples([
        """i("sql:")""",
        """i("sql:SELECT *  FROM (VALUES (1, 'red')) AS colors(id, color)")""",
        """
[
      i("https://rickandmortyapi.com/api/character/%s" % id) + 
      {image: i(super.image+"?awk_download=data/"+std.strReplace(std.asciiLower(super.name), " ", "_")+".jpeg")} + 
      {episode:: [i(episode) for episode in super.episode]} +
      {location:: ""} +
      {origin:: ""}
     for id in std.range(1,10)
]
        """
     ],
                inputs=[expression]
     )
    submit_btn = gr.Button("Interpret")
    result = gr.DataFrame()
    submit_btn.click(fn=predict_as_dataframe, inputs=expression, outputs=result, api_name="interpret")

