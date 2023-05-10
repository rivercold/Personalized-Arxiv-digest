"""
run:
python -m relevancy generate_relevance_score \
  --output_dir ./data \
  --model_name="gpt-3.5-turbo" \
"""
import time
import json
import os
import random
import re
import string
from datetime import datetime

import numpy as np
import tqdm
import utils

import fire
import pdb


def encode_prompt(query, prompt_papers):
    """Encode multiple prompt instructions into a single string."""
    prompt = open("./relevancy_prompt.txt").read() + "\n"

    for idx, task_dict in enumerate(prompt_papers):
        (title, authors, abstract) = task_dict["title"], task_dict["authors"], task_dict["abstract"]
        if not title:
            raise
        prompt += f"###\n"
        prompt += f"{idx + 1}. Title: {title}\n"
        prompt += f"{idx + 1}. Authors:\n{authors}\n"
        prompt += f"{idx + 1}. Abstract:\n{abstract}\n"
    prompt += f"\n Generate response:\n"
    print (prompt)
    return prompt


def post_process_chat_gpt_response(num_prompt_agents, response):
    print ("post_process_gpt_response")
    if response is None:
        return []
    raw_instructions = f"{num_prompt_agents+1}. Name:" + response['message']['content']
    raw_instructions = re.split("###", raw_instructions)
    agents = []
    for idx, inst in enumerate(raw_instructions):
        # if the decoding stops due to length, the last example is likely truncated so we discard it
        if idx == len(raw_instructions) - 1 and response["finish_reason"] == "length":
            continue
        idx += num_prompt_agents + 1
        splitted_data = re.split(f"{idx}\.\s+(Name|Goal):", inst)
        if len(splitted_data) != 5:
            continue
        else:
            name = splitted_data[2].strip()
            goal = splitted_data[4].strip()
        # filter out too short or too long role
        if len(goal.split()) <= 3 or len(goal.split()) > 150:
            continue
        # filter based on keywords that are not suitable for language models.
        # filter those starting with punctuation
        if goal[0] in string.punctuation:
            continue
        # filter those starting with non-english character
        if not goal[0].isascii():
            continue
        agents.append({"name": name, "goal": goal})
    return agents


def find_word_in_string(w, s):
    return re.compile(r"\b({0})\b".format(w), flags=re.IGNORECASE).search(s)


def process_subject_fields(subjects):
    all_subjects = subjects.split(";")
    all_subjects = [s.strip() for s in all_subjects]
    return all_subjects

def generate_relevance_score(
    query={"interest":"", "subjects":["Computation and Language (cs.CL)", "Artificial Intelligence (cs.AI)"]},
    date=None,
    output_dir="./data",
    model_name="gpt-3.5-turbo",
    num_paper_in_prompt=8,
    temperature=1.0,
    top_p=1.0,
):
    if date is None:
        date = datetime.today().strftime('%a, %d %b %y')
        # string format such as Wed, 10 May 2023
    print ("the date for the arxiv data is: ", date)

    all_papers = [json.loads(l) for l in open(f"{output_dir}/{date}.jsonl", "r")]
    print (f"We found {len(all_papers)}.")

    all_papers_in_subjects = [
        t for t in all_papers
        if bool(set(process_subject_fields(t['subjects'])) & set(query['subjects']))
    ]
    print(f"After filtering subjects, we have {len(all_papers_in_subjects)} papers left.")

    # now let's generate new instructions!
    # for loop iterating all_papers_in_subjects in tqdm, each time we take num_paper_in_prompt papers

    for request_idx in tqdm.tqdm(range(0, len(all_papers_in_subjects), num_paper_in_prompt)):
        prompt_papers = all_papers_in_subjects[request_idx:request_idx+num_paper_in_prompt]
        # only sampling from the seed tasks
        prompt = encode_prompt(query, prompt_papers)

        decoding_args = utils.OpenAIDecodingArguments(
            temperature=temperature,
            n=1,
            max_tokens=1072,  # hard-code to maximize the length. the requests will be automatically adjusted
            top_p=top_p,
        )
        request_start = time.time()
        results = utils.openai_completion(
            prompts=prompt,
            model_name=model_name,
            batch_size=1,
            decoding_args=decoding_args,
            logit_bias={"100257": -100},  # prevent the <|endoftext|> from being generated
            # "100265":-100, "100276":-100 for <|im_end|> and <endofprompt> token 
        )
        request_duration = time.time() - request_start

        # process_start = time.time()
        # relevance_data = post_process_chat_gpt_response(results)

        print(f"Request {request_idx+1} took {request_duration:.2f}s")
        pdb.set_trace()


def main(task, **kwargs):
    globals()[task](**kwargs)


if __name__ == "__main__":
    fire.Fire(main)