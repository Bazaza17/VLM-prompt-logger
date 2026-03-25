# VLM Prompt Testing Pipeline

A lightweight tool for testing Vision Language Model (VLM) prompts against video footage and automatically logging results to a Notion database. Built on Google Cloud Platform using Vertex AI and Gemini.

---

## What It Does

- Sends a prompt + video to a Gemini VLM model on Vertex AI
- Captures the model output and response time
- Automatically evaluates the output against an industry reference document
- Logs everything (prompt, output, time, detailed evaluation, summary) to a Notion database

---

## Stack

- **Google Colab** — runtime environment
- **Vertex AI** — model hosting and inference
- **Google Cloud Storage (GCS)** — video storage
- **Gemini** — Vision Language Model
- **Notion API** — experiment logging

---

## Setup

### 1. GCS Bucket
Upload your video files to a GCS bucket. Update `BUCKET_NAME` and `VIDEO_URI` in the script.

### 2. Vertex AI
Make sure your Colab runtime has access to your GCP project with Vertex AI enabled.

### 3. Notion Database
Create a Notion database with the following columns:

| Column | Type |
|---|---|
| Experiment Name | Title |
| Experiment Date | Date |
| Video Path | Text |
| Video Length | Text |
| Model Name | Text |
| Prompt | Text |
| Time to Output | Text |
| Output | Text |
| Comments | Text |
| Comment Summary | Text |

Then:
1. Go to [notion.so/my-integrations](https://notion.so/my-integrations) and create a new integration
2. Copy the integration token
3. Open your database → `...` → Connections → add your integration
4. Copy the database ID from the URL

### 4. Industry Reference Doc
Create a file called `industry_doc.txt` in the same directory as the script. This should contain domain-specific terminology and defect definitions relevant to your video content. The model uses this to evaluate VLM output accuracy.

> **Note:** Do not commit `industry_doc.txt` to GitHub if it contains proprietary information. It is included in `.gitignore`.

### 5. Configure the Script
Update the following variables at the top of the script:

```python
BUCKET_NAME = "your-bucket-name"
VIDEO_URI = "gs://your-bucket-name/your-video-folder/your-video.mp4"
VIDEO_LENGTH = "1:32"
MODEL_NAME = "gemini-2.5-flash"
NOTION_TOKEN = "your-notion-integration-token"
DATABASE_ID = "your-notion-database-id"
```

---

## Usage

1. Open the script in Google Colab
2. Run the GCS mount cell once at the start of your session
3. Update `prompt` in Cell 1 to your test prompt
4. Run Cell 1 — this sends the prompt to the VLM and prints the output
5. Run Cell 2 — this evaluates the output against your reference doc and logs everything to Notion
6. Repeat for each prompt, the experiment name auto-increments

---

## File Structure

```
vlm-prompt-testing/
├── vlm_test_template.py   # Main script
├── industry_doc.txt       # Your domain reference doc (not committed)
├── .gitignore
└── README.md
```

---

## Notes

- Output is truncated to 2000 characters in Notion due to API limits
- The run counter auto-increments by checking existing rows in the Notion database
- Experiment date auto-fills to today's date on each run
- The evaluation prompts use your `industry_doc.txt` as ground truth — the more detailed your reference doc, the better the evaluations
