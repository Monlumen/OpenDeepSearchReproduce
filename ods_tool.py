from smolagents import Tool, LiteLLMModel
from ods_agent import OpenSearchToolAgent

class OpenSearchTool(Tool):
    name="web_search"
    description="Performs web search based on your query (think a google search) then returns the final asnwer that is processed by an LLM"
    inputs={
        "query": {
            "type": "string",
            "description": "The search query to perform"
        }
    }
    output_type="string"

    def __init__(self, model_name: str, num_scrapes: int=2, pro_mode:bool=True, serper_api_key: str=None, jina_api_key: str=None):
        super().__init__()
        self.agent = OpenSearchToolAgent(model_name, serper_api_key, jina_api_key)
        self.num_scrapes = num_scrapes
        self.pro_mode = pro_mode
    
    def forward(self, query: str) -> str:
        return self.agent.ask_sync(query, self.num_scrapes, self.pro_mode)
    
    
if __name__ == "__main__":
    from smolagents import CodeAgent

    model_names = {
        "llama": "openrouter/meta-llama/llama-4-scout",
        "deepseek": "openrouter/deepseek/deepseek-r1"
    }
    model_name = model_names["llama"]

    agent = CodeAgent(
        tools=[OpenSearchTool(model_name)],
        model=LiteLLMModel(model_id=model_name),
        additional_authorized_imports=["numpy"],
        max_steps=15
    )

    result = agent.run("If my future wife has the same first name as the 15th first lady of the United States' mother and her surname is the same as the second assassinated president's mother's maiden name, what is my future wife's name?")
