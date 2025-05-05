import requests
import json
import dotenv
import os


dotenv.load_dotenv()
JINA_TRAIN_BASE_URL = "https://api.jina.ai/v1/train"
class JinaTrainer:

    def __init__(self, jina_api_key: str=None, jina_base_url: str=JINA_TRAIN_BASE_URL) -> None:
        self.data = []
        self.jina_api_key = jina_api_key or os.getenv("JINA_API_KEY")
        self.jina_base_url = jina_base_url
    
    def load_data(self, path: str = "./value_examples.jsonl"):
        with open(path, "r", encoding="utf-8") as f:
            self.data += [json.loads(line.strip()) for line in f if line.strip()]

    def train(self, epochs: int = 10) -> str:
        assert self.data
        self.data = [{"text": dict["text"][:1000], "label": dict["label"]} for dict in self.data]
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.jina_api_key
        }
        payload = {
            "model": "jina-embeddings-v3",
            "access": "private",
            "num_iters": epochs,
            "input": self.data
        }
        conversation = requests.post(
            self.jina_base_url,
            headers = headers,
            json = payload
        )
        conversation.raise_for_status()
        return conversation.text

    
if __name__ == "__main__":
    trainer = JinaTrainer()
    trainer.load_data()
    print(trainer.train())