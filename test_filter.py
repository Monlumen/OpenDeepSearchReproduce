from context_shaping.scraper_utils import default_text_filter
from jina_training.JinaTrainerDirect import JinaTrainer

filter = default_text_filter
trainer = JinaTrainer()
trainer.load_data()
data = trainer.data
filtered_data = set(filter.filter([dict["text"] for dict in data]))

accurate_num = 0
for entry in data:
    print("----------------")
    print(entry["text"][:50])
    print(entry["label"], entry["text"] in filtered_data)
    if ("Useful" in entry["label"]) == (entry["text"] in filtered_data):
        accurate_num += 1

print("accuracy: ", accurate_num / len(data))