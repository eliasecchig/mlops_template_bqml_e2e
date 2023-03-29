import os

import yaml
from kfp import dsl
from kfp import compiler

from utils.components.bigquery.sql_query import bq_sql_query_op

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
config = yaml.safe_load(open(f"{CURRENT_DIR}/config.yaml"))


@dsl.pipeline(
    name=config['pipeline_name'],
    description="Trains and deploys bqml model",
)
def bqml_pipeline(
        project: str,
        region: str = 'us-central1',
        parameters: dict = config.get("parameters")
):
    feature_eng_op = bq_sql_query_op(
        project=project,
        location=region,
        query=open(f"{CURRENT_DIR}/sql/00_feature_engineering.sql").read(),
        query_job_config={
            "destination": "{{ project }}.tx.feature_table_scoring",
            "write_disposition": "WRITE_TRUNCATE"
        },
        jinja_variables=parameters
    ).set_display_name('Feature engineering')

    scoring_op = bq_sql_query_op(
        project=project,
        location=region,
        query=open(f"{CURRENT_DIR}/sql/01_predict.sql").read(),
        query_job_config={
            "destination": "{{ project }}.tx.model_scores",
            "write_disposition": "WRITE_APPEND"
        },
        jinja_variables=parameters
    ).set_display_name('Model scoring').after(feature_eng_op)


if __name__ == '__main__':
    compiler.Compiler().compile(pipeline_func=bqml_pipeline, package_path="pipeline.yaml")
