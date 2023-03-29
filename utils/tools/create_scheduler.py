import json
import logging
from argparse import ArgumentParser

import yaml
from google.cloud import scheduler


def delete_scheduler_job(project: str, job_id: str, location="us-central1", stop_if_not_exist=False):
    client = scheduler.CloudSchedulerClient()
    job = f"projects/{project}/locations/{location}/jobs/{job_id}"
    try:
        logging.info(f"Deleting job {job}")
        client.delete_job(name=job, timeout=2)
        logging.info("Job deleted.")
    except Exception as e:
        logging.info(str(e))
        if stop_if_not_exist:
            raise e


def create_scheduler_job_to_pubsub(project: str, pubsub_topic_name: str, schedule: str, job_name: str, body: dict,
                                   timezone: str, location: str = "us-central1"):
    client = scheduler.CloudSchedulerClient()
    parent = f"projects/{project}/locations/{location}"
    pubsub_topic_resource = f"projects/{project}/topics/{pubsub_topic_name}"
    job_name = f"{parent}/jobs/{job_name}"
    job = {
        "pubsub_target": {
            "topic_name": pubsub_topic_resource,
            "data": json.dumps(body).encode(),
        },
        "name": job_name,
        "schedule": schedule,
        "time_zone": timezone,
    }
    response = client.create_job(request={"parent": parent, "job": job})
    logging.info("Created job: {}".format(response.name))
    return response


def get_args():
    parser = ArgumentParser()
    parser.add_argument("--config_path", help="Pipeline config", type=str)
    parser.add_argument(
        "--project", help="Project", type=str, required=True
    )
    parser.add_argument(
        "--location", help="Location", type=str, default="us-central1"
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    args = get_args()
    config = yaml.safe_load(open(args.config_path))
    delete_scheduler_job(
        project=args.project,
        job_id=config['pipeline_name'],
        location=args.location
    )
    create_scheduler_job_to_pubsub(
        project=args.project,
        pubsub_topic_name="trigger-vertex-pipeline",
        location=args.location,
        job_name=config['pipeline_name'],
        body={"pipeline_name": f"{config['pipeline_name']}/latest"},
        timezone=config["timezone"],
        schedule=config["pipeline_schedule"]
    )

