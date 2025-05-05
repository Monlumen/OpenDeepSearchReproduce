# OpenDeepSearchReproduce

## Running the FRAMES Benchmark

To run the FRAMES benchmark, first execute `evals/run_tasks.py`, followed by `evals/eval_tasks.py`. 

## Running the User Interface

I have designed a user interface from scratch using Gradio. To run this UI, simply execute `ui_demo.py`.

## Key Differences

Compared to the original work, this implementation presents the following key differences:

- **Model Selection:** I have opted for Gemini 2.5 Flash as the default model instead of Deepseek-R1. This change has significantly boosted the execution speed.
- **Content Filtering:** I have trained a Jina classifier to filter out texts with low educational value, replacing the fasttext approach used in the original work. The dataset used for training is stored at `value_examples.py`.