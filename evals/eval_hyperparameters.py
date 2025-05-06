
model_dict = {
    "llama": "openrouter/meta-llama/llama-4-scout",
    "deepseek": "openrouter/deepseek/deepseek-r1",
    "gemini2.5flash": "openrouter/google/gemini-2.5-flash-preview",
    "gemini2flash": "openrouter/google/gemini-2.0-flash-001"
}

base_model = model_dict["gemini2flash"]
n_threads = 8
n_trials = 3

testset_name = "test"