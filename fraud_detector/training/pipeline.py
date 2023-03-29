import os

import yaml
from kfp import dsl
from kfp import compiler

from utils.components.bigquery.extract_metrics_from_model import extract_metrics_from_model_op
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
                "destination": "{{ project }}.tx.feature_table",
                "write_disposition": "WRITE_TRUNCATE"
            },
        jinja_variables=parameters
    ).set_display_name('Feature engineering')

    bq_model_op = bq_sql_query_op(
        project=project,
        location=region,
        query=open(f"{CURRENT_DIR}/sql/01_train_model.sql").read(),
        jinja_variables=parameters
    ).after(feature_eng_op).set_display_name('Model training')

    evaluate_op = extract_metrics_from_model_op(
        project=project,
        location=region,
        model_name=bq_model_op.outputs['destination']
    ).after(bq_model_op)

    explain_op = bq_sql_query_op(
        project=project,
        location=region,
        query=open(f"{CURRENT_DIR}/sql/02_predict_explain.sql").read(),
        query_job_config={
            "destination": "{{ project }}.tx.explanations",
            "write_disposition": "WRITE_TRUNCATE"
        },
        jinja_variables=parameters
    ).after(bq_model_op).set_display_name('Model explain')

if __name__ == '__main__':
    compiler.Compiler().compile(pipeline_func=bqml_pipeline, package_path="pipeline.yaml")
