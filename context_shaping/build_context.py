from .Serper import SearchSources

def build_answer_box(sources: SearchSources) -> str:
    lines = []
    if sources.answer_box:
        for key in ["answer", "snippet"]: # "title", "answer", "snippet"
            if key in sources.answer_box:
                lines += [sources.answer_box[key]]
    if lines:
        return "\n".join(["ANSWER BOX"] + lines)
    return ""

def build_organic(sources: SearchSources) -> str:
    lines = []
    for entry in sources.organic:
        if "snippet" in entry:
            lines += ["title: " + entry.get("title", "N/A"),
                      "date authored: " + entry.get("date", "N/A"),
                      "link: " + entry.get("link", "N/A"),
                      "snippet: " + entry["snippet"]]
            if "html" in entry:
                lines += ["additional information: " + entry["html"]]
    if lines:
        return "\n".join(["SEARCH RESULTS:"] + lines)
    return ""

def build_top_stories(sources: SearchSources) -> str:
    if sources.top_stories:
        return "\n".join(["TOP STORIES", sources.top_stories])
    return ""

def build_context(sources: SearchSources) -> str:
    return "\n\n".join([box for box in [build_answer_box(sources), build_organic(sources), build_top_stories(sources)] if box])
