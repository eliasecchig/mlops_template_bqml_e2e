
training-pipeline:
	PYTHONPATH=. python fraud_detector/training/pipeline.py  && \
    python utils/tools/trigger_pipeline.py \
    --config_path fraud_detector/training/config.yaml \
    --project ${PROJECT_ID}

batch-scoring-pipeline:
    PYTHONPATH=. python fraud_detector/batch_scoring/pipeline.py  && \
    python utils/tools/trigger_pipeline.py \
    --config_path fraud_detector/batch_scoring/config.yaml \
    --project ${PROJECT_ID}