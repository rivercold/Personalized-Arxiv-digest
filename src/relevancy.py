"""
run:
python -m relevancy run_all_day_paper \
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


def post_process_chat_gpt_response(paper_data, response, threshold_score=8):
    print ("post_process_gpt_response")
    data = []
    if response is None:
        return []
    score_items = response['message']['content'].split("\n\n")
    # match the score 4 from the format of Relevancy score: 4/10. \n
    scores = [int(re.findall(r"Relevancy score: (\d+)", score_item)[0]) for score_item in score_items]
    try:
        assert len(score_items) == len(paper_data) == len(scores)
    except:
        print ("There are some parsing issue. ")
        pdb.set_trace()
    for idx, inst in enumerate(score_items):
        # if the decoding stops due to length, the last example is likely truncated so we discard it
        if scores[idx] < threshold_score:
            continue
        output_str = "Title: " + paper_data[idx]["title"] + "\n"
        output_str += "Authors: " + paper_data[idx]["authors"] + "\n"
        output_str += score_items[idx].strip(f"{idx+1}.")
        data.append(output_str)
    return data


def find_word_in_string(w, s):
    return re.compile(r"\b({0})\b".format(w), flags=re.IGNORECASE).search(s)


def process_subject_fields(subjects):
    all_subjects = subjects.split(";")
    all_subjects = [s.strip() for s in all_subjects]
    return all_subjects

def generate_relevance_score(
    all_papers,
    query,
    model_name="gpt-3.5-turbo",
    threshold_score=8,
    num_paper_in_prompt=4,
    temperature=1.0,
    top_p=1.0,
):
    ans_data = []
    for request_idx in tqdm.tqdm(range(0, len(all_papers), num_paper_in_prompt)):
        prompt_papers = all_papers[request_idx:request_idx+num_paper_in_prompt]
        # only sampling from the seed tasks
        prompt = encode_prompt(query, prompt_papers)

        decoding_args = utils.OpenAIDecodingArguments(
            temperature=temperature,
            n=1,
            max_tokens=1072,  # hard-code to maximize the length. the requests will be automatically adjusted
            top_p=top_p,
        )
        request_start = time.time()
        response = utils.openai_completion(
            prompts=prompt,
            model_name=model_name,
            batch_size=1,
            decoding_args=decoding_args,
            logit_bias={"100257": -100},  # prevent the <|endoftext|> from being generated
            # "100265":-100, "100276":-100 for <|im_end|> and <endofprompt> token 
        )
        print(response)
        request_duration = time.time() - request_start

        process_start = time.time()
        batch_data = post_process_chat_gpt_response(prompt_papers, response, threshold_score=threshold_score)
        ans_data.extend(batch_data)

        print(f"Request {request_idx+1} took {request_duration:.2f}s")
        print(f"Post-processing took {time.time() - process_start:.2f}s")
    return ans_data

def run_all_day_paper(
    query={"interest":"", "subjects":["Computation and Language", "Artificial Intelligence"]},
    date=None,
    output_dir="./data",
    model_name="gpt-3.5-turbo",
    num_paper_in_prompt=8,
    temperature=1.0,
    top_p=1.0
):
    if date is None:
        date = datetime.today().strftime('%a, %d %b %y')
        # string format such as Wed, 10 May 23
    print ("the date for the arxiv data is: ", date)

    all_papers = [json.loads(l) for l in open(f"{output_dir}/{date}.jsonl", "r")]
    print (f"We found {len(all_papers)}.")

    all_papers_in_subjects = [
        t for t in all_papers
        if bool(set(process_subject_fields(t['subjects'])) & set(query['subjects']))
    ]
    print(f"After filtering subjects, we have {len(all_papers_in_subjects)} papers left.")
    ans_data = generate_relevance_score(all_papers_in_subjects, query, model_name, num_paper_in_prompt, temperature, top_p)
    
    return ans_data


def main(task, **kwargs):
    globals()[task](**kwargs)
