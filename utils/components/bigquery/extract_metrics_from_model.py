
from kfp import dsl
from kfp.dsl import Output, Metrics


@dsl.component(
    base_image="gcr.io/ml-pipeline/google-cloud-pipeline-components:2.0.0b0",
)
def extract_metrics_from_model_op(
        project: str,
        location: str,
        model_name: str,
        metrics: Output[Metrics]
):
    from google.cloud import bigquery

    client = bigquery.client.Client(project=project, location=location)
    df = client.query(f" SELECT * FROM ML.EVALUATE(MODEL `{model_name}`)").to_dataframe()
    for metric, value in df.iloc[0].to_dict().items():
        metrics.log_metric(metric, value)

