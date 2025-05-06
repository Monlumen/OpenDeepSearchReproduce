import gradio as gr
from ods_tool import OpenSearchTool
from smolagents import CodeAgent, LiteLLMModel, ActionStep, FinalAnswerStep
import pandas as pd
from datasets import Dataset
import re
import random

examples = []
def load_examples(path = "./evals/datasets/frames_test_set.csv"):
    pd_table = pd.read_csv(path)
    dataset = Dataset.from_pandas(pd_table)
    examples = [entry for entry in dataset][1:]
    return examples
examples = load_examples()

def pick_random_example():
    random.shuffle(examples)
    return examples[0]

with gr.Blocks() as demo:
    gr.Markdown("## Open Deep Search")
    history = gr.State([])
    running = gr.State(False)
    time_elapsed = gr.State(0)
    dataset_answer = gr.State("")
    with gr.Row():
        with gr.Column():
            query = gr.Textbox(label="Query")
            with gr.Row():
                grab_btn = gr.Button("Grab one from FRAMES")
                @gr.render(inputs=[dataset_answer])
                def render_ds_answer(dataset_answer):
                    if dataset_answer:
                        gr.Markdown("### Golden Answer: " + dataset_answer)
                def on_grab_btn_click():
                    example = pick_random_example()
                    return example["question"], example["true_answer"]
                grab_btn.click(on_grab_btn_click, [], [query, dataset_answer])

            submit_btb = gr.Button(value="Search!", variant="primary")
        with gr.Column():
            radio = gr.Radio(["Snap", "Pro"], value="Snap", label="Mode", info="How hard should I think?")
            @gr.render(inputs=[radio])
            def render_mode_desc(mode: str):
                text = ""
                if mode == "Snap":
                    text = "OpenSearchTool + CodeAct + Gemini2-Flash"
                elif mode == "Pro":
                    text = "OpenSearchTool(Pro Mode) + CodeAct + Gemini2-Flash"
                else:
                    text = "OpenSearchTool(Pro Mode) + CodeAct + Deepseek-R1" + "\n(It might take several minutes)"
                gr.Text(text, label="")

    timer_interval = 0.1
    timer = gr.Timer(timer_interval)
    timer.tick(lambda x, running: x+timer_interval*running, (time_elapsed, running), time_elapsed)

    @gr.render(inputs=[history])
    def render_history(history):
        def try_render_final_step(final_step):
            if final_step and isinstance(final_step, FinalAnswerStep):
                gr.Label("🌟 " + str(final_step.final_answer))
        final_step = history[-1] if (history and isinstance(history[-1], FinalAnswerStep)) else None
        try_render_final_step(final_step)
        for idx, step in enumerate(history):
            gr.Markdown(f"### Step {idx + 1}")
            if isinstance(step, ActionStep):
                thought = step.model_output.split("```")[0]
                thought = re.sub("Thought:", "**Thought:**", thought)
                thought = re.sub("Code:", "**Code:**", thought)
                gr.Markdown("🤖" + thought)
                codes = re.findall(r"```(?:py|python)\n((?:.*\n)*)?```", step.model_output, (re.IGNORECASE | re.DOTALL))
                for code in codes:
                    gr.Code(code, "python")
                if codes and step.observations:
                    obs = step.observations
                    obs = re.sub("Execution logs:", "**Execution logs:**", obs)
                    obs = re.sub("Last output from code snippet:.*\n.*", "", obs)
                    gr.Markdown("💻" + obs)
                gr.HTML("<hr>")
        try_render_final_step(final_step)

    @gr.render(inputs=[running, time_elapsed])
    def render_running(running, time_elapsed):
        if running:
            gr.Markdown(f"### 🤖Thinking Hard~({time_elapsed:.1f}s)")
    
    def ask(query: str, mode: str):
        if mode == "Snap":
            model = "openrouter/google/gemini-2.0-flash-001"
            pro_mode = False
        elif mode == "Pro":
            model = "openrouter/google/gemini-2.0-flash-001"
            pro_mode = True
        else:
            model = "openrouter/deepseek/deepseek-r1"
            pro_mode = True

        history = []
        yield history, True, 0
        agent = CodeAgent(
            [OpenSearchTool(model, pro_mode=pro_mode)],
            model=LiteLLMModel(model),
            additional_authorized_imports=["numpy"],
            max_steps=20
        )
        for step in agent.run(query, stream=True):
            history += [step]
            yield history, (not isinstance(step, FinalAnswerStep)), 0

    submit_btb.click(ask, [query, radio], [history, running, time_elapsed])
    

demo.queue(default_concurrency_limit=5)
demo.launch()