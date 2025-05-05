import re
from .regular_expressions import ads_pattern, meta_pattern_weak, meta_pattern_strong
import fasttext
from huggingface_hub import hf_hub_download
from typing import Union, List
from .hyper_parameters import debug
from .TextFilter import TextFilter, JinaTextFilter

default_text_filter = JinaTextFilter()

# hypothethis: 2 chinese characters = 1 english word
def count_words(text: str) -> int:
    words = text.split()
    word_count = len(words)
    for word in words:
        n_chinese_characters = len(re.findall(r'[\u4e00-\u9fff]', word))
        if n_chinese_characters > 2:
            word_count += (n_chinese_characters - 2) / 2
    return word_count

# 根据[PAGE_INDEX], 我们知道....., 又根据[PAGE_INDEX], 所以答案是.....
def clean_text(text: str) -> str:
    results = []
    paragraphs = text.split("\n\n")
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if "```" in paragraph:
            results.append(paragraph)
            continue
        lines = []
        for line in paragraph.split("\n"):
            if not line:
                continue
            if re.match(r"^#{1,6}\s+", line):
                lines.append(line)
            if re.match(ads_pattern, line, re.IGNORECASE):
                continue
            line_pure_text = re.sub(meta_pattern_weak, "", line) 
            if count_words(line_pure_text) < 12:  # TODO: Chinese Support
                line_really_pure_text = re.sub(meta_pattern_strong, "", line)
                if count_words(line_really_pure_text) < 8:
                    continue
            lines.append(line)
        if lines:
            results.append("\n".join(lines))
    return "\n\n".join(results)

def filter_text_by_value(text: str, text_filter: TextFilter=default_text_filter) -> str:
    return "\n\n".join(text_filter.filter(text.split("\n\n")))

if __name__ == "__main__":
    text = [
        "subscribe to our podcast for the latest tech news!",
        "join our member club to get the cheapest goods on the market",
        "joe biden, elected as US President in 2020, was the eldest president ever at that time",
        "huggingface is a good company"
    ]