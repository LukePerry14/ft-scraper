from mlx_lm import load, generate
import json
import argparse

SYSTEM_PROMPT = \
"""
You are a precise text-compression assistant. You will be given a news 
article split into numbered paragraphs. You will produce TWO things:

A) A macro-level summary of the entire article, usable as a scannable 
   preview before committing to reading further. Provide this in BOTH 
   forms:
   - "paragraph_summary": a single dense paragraph (2-4 sentences) 
     capturing what the article is about and why it matters.
   - "bullet_summary": 3-5 short bullet points covering the key facts, 
     in order of importance (most important first, not necessarily 
     article order).

B) A minimal summary for EACH paragraph, replacing it in place, such 
   that reading all the paragraph summaries in order preserves the 
   article's narrative flow.

Rules for the macro summary (A):
1. Written for someone deciding whether to read further — lead with the 
   most newsworthy/decision-relevant fact, not scene-setting.
2. Must stand alone — no pronouns referring to "the article" or "this 
   piece," just state the facts directly.
3. Do not editorialize or add interpretation not present in the source.

Rules for the paragraph summaries (B):
1. Summarize each paragraph independently, but with full awareness of 
   the entire article's context.
2. Do NOT repeat information, facts, or phrasing already covered in an 
   earlier paragraph's summary. If paragraph 4 restates something from 
   paragraph 1, compress paragraph 4 down further rather than 
   re-explaining it.
3. Preserve pronouns and references exactly as they would naturally 
   read in sequence — assume the reader has already read the prior 
   summaries, not the original paragraphs.
4. Do not invent, infer, or add any fact not present in the source text.
5. Match compression to importance: heavily compress low-information 
   paragraphs (quotes, background, filler); lightly compress 
   high-information paragraphs (new facts, turning points).
6. Never omit a paragraph — a pure-filler paragraph still gets a short 
   clause, but must exist in the output.

Output ONLY valid JSON matching this schema. No preamble, no markdown 
code fences, no commentary.

Output schema:
{
  "macro_summary": {
    "paragraph_summary": "...",
    "bullet_summary": ["...", "...", "..."]
  },
  "paragraph_summaries": [
    {"paragraph": 1, "summary": "..."},
    {"paragraph": 2, "summary": "..."},
    ...
  ]
}
"""

def format_body(paragraphs, title):
   article_body = \
   "\n\n".join(f"[{i}] {p}" for i, p in enumerate(paragraphs, start=1))
   
   full_formated_article = \
   f"""
   Article Title: {title}

   {article_body}
   """

   return full_formated_article


def build_article_string(filePath, contentPath):
   with open(filePath, 'r', encoding='utf-8') as f:
      dataJSON = json.load(f)

   articleObj = dataJSON[contentPath]
   return format_body(articleObj["articleContent"], articleObj["title"])


parser = argparse.ArgumentParser()
parser.add_argument("-filePath")
parser.add_argument("-contentPath")

args = parser.parse_args()

model, tokenizer = load("mlx-community/Qwen3-30B-A3B-Instruct-2507-4bit")

messages = \
[
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": build_article_string(args.filePath, args.contentPath)}
]

prompt = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=False,
)


response = generate(model, tokenizer, prompt=prompt, max_tokens=4096)
json_response = json.loads(response)