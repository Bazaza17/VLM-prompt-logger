# -*- coding: utf-8 -*-
"""VLM Prompt Testing Pipeline
A tool for testing and logging VLM prompts against utility inspection videos.
Automatically logs results, response times, and industry-reference evaluations to Notion.

Setup:
1. Mount your GCS bucket (update BUCKET_NAME)
2. Add your Notion token and database ID
3. Add your industry reference doc as industry_doc.txt
4. Update VIDEO_URI to point to your video
5. Set your model name
"""

# ── 1. Mount GCS Bucket ───────────────────────────────────────────────────────
# Update BUCKET_NAME to your GCS bucket
BUCKET_NAME = "your-bucket-name"

# !sudo mkdir -p /gcs/{BUCKET_NAME} (FYI, remove #)
# !gcsfuse {BUCKET_NAME} --implicit-dirs /gcs/{BUCKET_NAME} (FYI, remove #)


# ── 2. Model & Video Setup ────────────────────────────────────────────────────
import vertexai
import time
from vertexai.generative_models import GenerativeModel, Part

# Update to your model name (e.g. "gemini-2.5-flash", "gemini-2.0-flash", etc.)
MODEL_NAME = "your-model-name"

# Update to your video path
VIDEO_URI = "gs://your-bucket-name/your-video-folder/your-video.mp4"
VIDEO_LENGTH = "0:00"  # e.g. "1:32"

model = GenerativeModel(MODEL_NAME)

video_part = Part.from_uri(
    uri=VIDEO_URI,
    mime_type="video/mp4"  # update if using a different format e.g. "video/quicktime"
)

# ── Prompt ────────────────────────────────────────────────────────────────────
# Replace with your prompt for this run
prompt = "Your prompt here."

start = time.time()
response = model.generate_content([video_part, prompt])
elapsed = str(round(time.time() - start)) + "s"

print(f"Time: {elapsed}")
print(response.text)


# ── 3. Notion Logging Setup ───────────────────────────────────────────────────
import requests

# Add your Notion integration token and database ID
# Get your token at: https://www.notion.so/my-integrations
NOTION_TOKEN = "your-notion-integration-token"
DATABASE_ID = "your-notion-database-id"

# Load industry reference doc for evaluation
# Create a file called industry_doc.txt in the same directory with your reference content
import os
if os.path.exists("industry_doc.txt"):
    with open("industry_doc.txt", "r") as f:
        INDUSTRY_DOC = f.read()
else:
    INDUSTRY_DOC = ""
    print("Warning: industry_doc.txt not found. Evaluations will be empty.")

# ── Notion Database Schema ────────────────────────────────────────────────────
# Your Notion database should have the following columns:
# - Experiment Name (title)
# - Experiment Date (date)
# - Video Path (text)
# - Video Length (text)
# - Model Name (text)
# - Prompt (text)
# - Time to Output (text)
# - Output (text)
# - Comments (text)
# - Comment Summary (text)

def log_to_notion(run_number, prompt, output, time_to_output="", comments="", comment_summary=""):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Experiment Name": {"title": [{"text": {"content": f"test_run_{run_number}"}}]},
            "Experiment Date": {"date": {"start": time.strftime("%Y-%m-%d")}},
            "Video Path": {"rich_text": [{"text": {"content": VIDEO_URI}}]},
            "Video Length": {"rich_text": [{"text": {"content": VIDEO_LENGTH}}]},
            "Model Name": {"rich_text": [{"text": {"content": MODEL_NAME}}]},
            "Prompt": {"rich_text": [{"text": {"content": prompt}}]},
            "Time to Output": {"rich_text": [{"text": {"content": time_to_output}}]},
            "Output": {"rich_text": [{"text": {"content": output[:2000]}}]},
            "Comments": {"rich_text": [{"text": {"content": comments[:2000]}}]},
            "Comment Summary": {"rich_text": [{"text": {"content": comment_summary[:2000]}}]},
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

def get_next_run_number():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28"
    }
    response = requests.post(url, headers=headers)
    results = response.json().get("results", [])
    return len(results) + 1


# ── 4. Evaluate & Log ─────────────────────────────────────────────────────────
run_number = get_next_run_number()

detailed_comment_prompt = f"""You are an expert in [your domain, e.g. hardware inspection, medical imaging, manufacturing QA, etc.].

Using the industry reference document below, evaluate the accuracy of the following VLM output in detail. Note any incorrect terminology, missed components, inaccurate observations, or correct identifications. Be thorough.

INDUSTRY REFERENCE:
{INDUSTRY_DOC}

VLM OUTPUT:
{response.text}
"""

summary_comment_prompt = f"""You are an expert in [your domain, e.g. hardware inspection, medical imaging, manufacturing QA, etc.].

Using the industry reference document below, provide a 2-3 sentence summary evaluation of the following VLM output. Was it accurate? What was the most important thing it got right or wrong?

INDUSTRY REFERENCE:
{INDUSTRY_DOC}

VLM OUTPUT:
{response.text}
"""

detailed_comment = model.generate_content(detailed_comment_prompt)
summary_comment = model.generate_content(summary_comment_prompt)

status = log_to_notion(
    run_number,
    prompt,
    response.text,
    elapsed,
    detailed_comment.text,
    summary_comment.text
)

print(f"Logged to Notion — run {run_number} — status: {status}")
print(f"\nSummary: {summary_comment.text}")


from IPython.display import display, Javascript
display(Javascript('''
// Note: This only works in Google Colab / Jupyter notebooks
var cells = Jupyter.notebook.get_cells();
for (var i = 0; i < cells.length; i++) {
    if (cells[i].get_text().includes("prompt =")) {
        cells[i].set_text('prompt = ""');
        break;
    }
}
'''))    
