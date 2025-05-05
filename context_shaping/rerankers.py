import requests
from abc import ABC, abstractmethod
from typing import List
import os
import dotenv
import torch
from tenacity import retry, stop_after_attempt, wait_fixed

dotenv.load_dotenv()

JINA_EMBEDDING_BASE_URL = 'https://api.jina.ai/v1/embeddings'
JINA_RERANK_BASE_URL = 'https://api.jina.ai/v1/rerank'

class Reranker(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def rerank(self, query: str, documents: List[str]) -> List[str]:
        pass

class JinaTorchReranker(Reranker):

    def __init__(self, jina_api_key: str=None, jina_base_url: str = JINA_EMBEDDING_BASE_URL):
        super().__init__()
        self.jina_api_key = jina_api_key or os.getenv("JINA_API_KEY")
        self.jina_base_url = jina_base_url
        assert self.jina_api_key

    def get_embedding(self, texts: List[str]) -> torch.Tensor:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.jina_api_key
        }
        payload = {
            "model": "jina-embeddings-v3",
            "task": "text-matching",
            "input": texts,
            "truncate": True
        }
        conversation = requests.post(self.jina_base_url, headers=headers, json=payload)
        conversation.raise_for_status()
        json = conversation.json()
        embeddings = [dict["embedding"] for dict in json["data"]]
        return torch.tensor(embeddings, requires_grad=False)
    
    @torch.no_grad
    def rerank(self, query:str, documents: List[str], top_k: int=5) -> List[str]:
        if not documents:
            return []
        query_matrix = self.get_embedding([query])
        documents_matrix = self.get_embedding(documents)
        scores = query_matrix @ documents_matrix.T
        values, indices = torch.topk(scores.reshape(-1), min(len(documents), top_k))
        return [documents[index] for index in indices]
    
class PureJinaReranker(Reranker):
    def __init__(self, jina_api_key: str=None, jina_base_url: str = JINA_RERANK_BASE_URL):
        super().__init__()
        self.jina_api_key = jina_api_key or os.getenv("JINA_API_KEY")
        self.jina_base_url = jina_base_url
    
    def rerank(self, query: str, documents: List[str], top_k: int=5) -> List[str]:
        try:
            return self._rerank(query, documents, top_k)
        except requests.HTTPError as e:
            return []

    # @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _rerank(self, query: str, documents: List[str], top_k: int=5) -> List[str]:
        if not documents:
            return []
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.jina_api_key
        }
        payload = {
            "model": "jina-reranker-v2-base-multilingual",
            "query": query,
            "top_n": min(top_k, len(documents)),
            "documents": documents,
            "return_documents": False
        }
        conversation = requests.post(self.jina_base_url, headers=headers, json=payload)
        conversation.raise_for_status()
        json = conversation.json()
        indices = [dict["index"] for dict in json["results"]]
        return [documents[index] for index in indices]

if __name__ == "__main__":
    reranker = PureJinaReranker()
    query = "CEO"
    documents = [
        "奥巴马",
        "Joe Biden", 
        "Tim Cook",
        "洗衣液",
        "少年PI的奇妙漂流",
        "Monlumen",
        "，温和滋润，保护您的肌肤不受刺激。让您的肌肤告别不适，迎来健康光彩。",
        "苹果"
    ]
    print(reranker.rerank(query, documents))