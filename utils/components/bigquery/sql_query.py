import logging
from typing import NamedTuple

from kfp import dsl


@dsl.component(
    base_image="gcr.io/ml-pipeline/google-cloud-pipeline-components:2.0.0b0",
    packages_to_install=["Jinja2==3.1.2"]
)
def bq_sql_query_op(
        project: str,
        location: str,
        query: str,
        jinja_variables: dict = {},
        query_job_config: dict = {},
        execution_timestamp: str = "",
) -> NamedTuple("Outputs", [("gcp_resources", str), ("destination", str), ("templated_sql_query", str)]):
    import jinja2
    import json
    import logging

    from google.cloud import bigquery
    from datetime import datetime
    from google_cloud_pipeline_components.proto.gcp_resources_pb2 import GcpResources
    from google.protobuf.json_format import MessageToJson
    from collections import namedtuple

    def render_string(string, **kwargs):
        GLOBALS_JINJA = {"now": datetime.utcnow}
        rtemplate = jinja2.Environment(loader=jinja2.BaseLoader).from_string(string)
        data = rtemplate.render(**kwargs, **GLOBALS_JINJA)
        return data

    def sql_query(
            project: str,
            location: str,
            sql_query: str,
            query_job_config: dict = {}
    ) -> bigquery.QueryJob:
        client = bigquery.client.Client(project=project, location=location)
        job_config = bigquery.QueryJobConfig(**query_job_config)
        query_job = client.query(sql_query, job_config=job_config)
        logging.info(query_job.result())
        return query_job

    jinja_variables = json.loads(render_string(
        json.dumps(jinja_variables),
    ))
    jinja_variables = {
        "project": project,
        "location": location,
        "execution_timestamp": execution_timestamp,
        **jinja_variables
    }
    query_job_config = json.loads(render_string(
        json.dumps(query_job_config),
        **jinja_variables
    ))
    templated_sql_query = render_string(
        query,
        **jinja_variables,
    )
    logging.info('-------------------TEMPLATED SQL QUERY: --------------------')
    logging.info(templated_sql_query.replace('\n', ''))
    query_job = sql_query(
        project=project,
        sql_query=templated_sql_query,
        location=location,
        query_job_config=query_job_config
    )
    # Returning job resource to integrate with BigQuery
    # https://cloud.google.com/vertex-ai/docs/pipelines/build-own-components
    bigquery_resources = GcpResources()
    br = bigquery_resources.resources.add()
    br.resource_type = 'BigQueryJob'
    br.resource_uri = f'https://www.googleapis.com/bigquery/v2/projects/{project}/jobs/{query_job.job_id}?location={location}'
    gcp_resources = MessageToJson(bigquery_resources)
    outputs = namedtuple('Outputs', ['gcp_resources', "destination", "templated_sql_query"])
    return outputs(gcp_resources, str(query_job.destination), templated_sql_query)
