# gcp-mlops-demo

This is a sample project that illustrates how to use [Vertex AI](https://cloud.google.com/vertex-ai) on GCP for building and running [MLOps workflows](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning#mlops_level_2_cicd_pipeline_automation).

## GCP environment setup
```commandline
bash utils/scripts/setup.sh
```

### Setup local environment
Setup environment:
```commandline
virtualenv venv && source venv/bin/activate && pip install -r requirements.txt
```

### Import training data
Run the following script to download the data in BQ:
```commandline
python utils/scripts/copy_bigquery_data.py --project $PROJECT_ID --location  "us-central1"
```

## Pipelines

### Trigger training pipeline
```commandline
make training-pipeline
```

### Trigger batch scoring pipeline
```commandline
make batch-scoring-pipeline
```

## CICD
Run Cloud build pipeline for training (training pipeline is default in Cloud Build)
```commandline
gcloud builds submit --config build/test_and_deploy_pipeline.yaml
```

Run Cloud build pipeline for batch scoring
```commandline
gcloud builds submit --config build/test_and_deploy_pipeline.yaml --substitutions="_PIPELINE_FOLDER=fraud_detector/batch_scoring"
```


### Create a repository 
We create a repository in Cloud Source repository to showcase how a commit can trigger Cloud Build
```commandline
REPOSITORY_NAME=fraud_detector
gcloud source repos create $REPOSITORY_NAME --project=$PROJECT_ID

git init && git config --global credential.https://source.developers.google.com.helper gcloud.sh
git remote add origin https://source.developers.google.com/p/$PROJECT_ID/r/$REPOSITORY_NAME
```

Please note that we copy the file for

You will need now to setup 2 triggers, for the 2 vertex pipelines you support.
You would like to achieve the following behaviour: 
- Every time a file under `fraud_detector/training` changes, you want to trigger a new deployment of CloudBuild for the batch scoring pipeline:
```
gcloud beta builds triggers create cloud-source-repositories \
    --name=fd-training \
    --repo=$REPOSITORY_NAME \
    --branch-pattern=main \
    --build-config=build/test_and_deploy_pipeline.yaml \
    --substitutions="_PIPELINE_FOLDER=fraud_detector/training" \
    --included-files="fraud_detector/training/*"
```
- Every time a file under `fraud_detector/batch_scoring` changes, you want to trigger a new deployment of CloudBuild for the batch scoring pipeline:
```
gcloud beta builds triggers create cloud-source-repositories \
    --name=fd-batch-scoring \
    --repo=$REPOSITORY_NAME \
    --branch-pattern=main \
    --build-config=build/test_and_deploy_pipeline.yaml \
    --substitutions="_PIPELINE_FOLDER=fraud_detector/batch_scoring" \
    --included-files="fraud_detector/batch_scoring/*"
```

Make your first commit
```commandline
cd $REPOSITORY_NAME && git add .
git config --global user.email "your_email"
git config --global user.name "your_email"
git commit -a -m "initial commit"
git push --set-upstream origin main
```




