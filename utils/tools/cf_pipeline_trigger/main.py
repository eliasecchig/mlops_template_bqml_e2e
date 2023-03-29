import os
import base64
import json
from google.cloud import aiplatform

REGION = os.environ["REGION"]
PROJECT_ID = os.environ["PROJECT_ID"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
PIPELINE_REPO_NAME = os.environ.get("PIPELINE_REPO_NAME","pipeline-repository")

def subscribe(event, context):
    payload_message = base64.b64decode(event['data']).decode('utf-8')
    print(payload_message)
    payload_json = json.loads(payload_message)
    pipeline_name = payload_json['pipeline_name']

    aiplatform.init(project=PROJECT_ID, location=REGION)

    job = aiplatform.PipelineJob(
        display_name=pipeline_name,
        template_path=f'https://{REGION}-kfp.pkg.dev/{PROJECT_ID}/{PIPELINE_REPO_NAME}/{pipeline_name}',
        location=REGION,
        project=PROJECT_ID,
        enable_caching=False,
        pipeline_root=f'gs://{BUCKET_NAME}',
        parameter_values={
            "project": PROJECT_ID,
            "region": REGION,
        }
    )

    job.submit()
