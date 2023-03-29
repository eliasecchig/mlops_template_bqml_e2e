import argparse
import os

from kfp.registry import RegistryClient


def parse_args():
    parser = argparse.ArgumentParser(description="Utility tool to upload pipeline templates")
    parser.add_argument("--pipeline_path", help="Pipeline path", required=False, default='pipeline.yaml')
    parser.add_argument("--project", help="Pipeline path", required=False, default=os.getenv("PROJECT_ID"))
    parser.add_argument("--region", help="Pipeline path", required=False, default="us-central1")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    client = RegistryClient(host=f"https://{args.region}-kfp.pkg.dev/{args.project}/pipeline-repository")
    template_name, template_version = client.upload_pipeline(
        file_name="pipeline.yaml",
        tags=["latest"]
    )
