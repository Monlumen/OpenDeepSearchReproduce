from ods_agent import OpenSearchToolAgent
import asyncio

def load_search_queries():
    with open("./search_queries.txt", "r") as f:
        queries = [line.strip() for line in f]
    return queries

agent = OpenSearchToolAgent("openrouter/deepseek/deepseek-r1")

queries = load_search_queries()

print(asyncio.run(agent.search_and_build_context(queries[100])))
