
model_dict = {
    "llama": "openrouter/meta-llama/llama-4-scout",
    "deepseek": "openrouter/deepseek/deepseek-r1",
    "gemini2.5flash": "openrouter/google/gemini-2.5-flash-preview"
}

base_model = model_dict["gemini2.5flash"]
n_threads = 8

testset_name = "test"