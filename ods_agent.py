from context_shaping.Serper import SerperAPI, SearchSources
from context_shaping.SourceProcessor import SourceProcessor
from context_shaping.build_context import build_context
from smolagents import LiteLLMModel
from litellm import completion
import asyncio
from prompts import SEARCH_SYSTEM_PROMPT
import nest_asyncio
from tenacity import retry, stop_after_attempt, wait_fixed

class OpenSearchToolAgent:
    def __init__(self, model_name: str, serper_api_key: str=None, jina_api_key: str=None):
        self.model = LiteLLMModel(model_name)
        self.serper = SerperAPI(serper_api_key)
        self.source_processor = SourceProcessor(jina_api_key)

    async def search_and_build_context(self, query: str, num_scrapes: int=2, pro_mode: bool=True) -> str:
        sources: SearchSources = self.serper.get_sources(query)
        sources = await self.source_processor.process_sources(sources, query, num_scrapes, pro_mode=pro_mode)
        return build_context(sources)
    
    async def ask(self, query: str, num_scrapes: int=2, pro_mode:bool=False) -> str:
        context = await self.search_and_build_context(query, num_scrapes, pro_mode)
        history = [
            {"role": "system", "content": SEARCH_SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:{query}"}
        ]
        @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
        def get_response(model_id, history):
            return completion(model_id, history)
        response = get_response(self.model.model_id, history)
        return response.choices[0].message.content

    def ask_sync(self, query: str, num_scrapes: int=2, pro_mode:bool=False) -> str:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                nest_asyncio.apply()
        except RuntimeError as e:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.ask(query, num_scrapes, pro_mode))

if __name__ == "__main__":
    agent = OpenSearchToolAgent("openrouter/meta-llama/llama-4-scout")
    print(agent.ask_sync("Which Dutch player scored an open-play goal in the 2022 Netherlands vs Argentina game in the men’s FIFA World Cup"))