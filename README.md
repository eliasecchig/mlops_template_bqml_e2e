# Dummy BQML system E2E implementation

This is a sample project that illustrates how to use [Vertex AI](https://cloud.google.com/vertex-ai), BQML and Cloud Build to
build a fully functional <b>ML system</b> comprising of the following functionalities:
- [Training Pipeline](fraud_detector/training/pipeline.py): implemented using Vertex AI Pipeline, we showcase a simple pipeline that executes BQML queries to train a model.
- [Batch scoring Pipeline](fraud_detector/batch_scoring/pipeline.py): similar to the training pipeline, also this pipeline is implemented using Vertex AI Pipeline. It will perform predictions for the BQML model. 
- [CICD Pipeline](cloudbuild/test_and_deploy_pipeline.yaml): implemented with Cloud Build, this pipeline will execute dummy unit tests, compile the pipelines, test them and then simulate a deployment to production with schedule enabled.  

As part of this repository we guide the user in setting up the system in a matter of minutes.
We will show how to execute training, scoring and how to setup CICD for both pipelines, by creating a dummy repository to allow for automatic trigger.

The system implemented in this repository is a dummy fraud detection model, implemented using the same dataset of [FraudFinder](https://github.com/GoogleCloudPlatform/fraudfinder)

## Supercharging BQML with Jinja

A key feature of the BQML queries defined in this repository is that they support [Jinja2 templating](https://jinja.palletsprojects.com/en/2.11.x/templates/).
This extends the capabilities of SQL by introducing scripting, allowing developers to define complex logic in the SQL such as:
- [For loops](https://jinja.palletsprojects.com/en/3.1.x/templates/#for)
- [If-else](https://jinja.palletsprojects.com/en/3.1.x/templates/#if) statements
- [Re-usable macros](https://jinja.palletsprojects.com/en/3.1.x/templates/#macros) and [Template Inheritance](https://jinja.palletsprojects.com/en/3.1.x/templates/#template-inheritance) to abstract and reuse complex logic
- SQL Parametrisation through configuration files

An example of that is the model name and model parameters of the SQL file which creates the model in `fraud_detector/training/sql/01_train_model.sql`:
```
CREATE OR REPLACE MODEL `{{ model_name }}`
        OPTIONS (
            MODEL_TYPE='LOGISTIC_REG',
            INPUT_LABEL_COLS=['tx_fraud'],
            EARLY_STOP=TRUE,
            MAX_ITERATIONS={{ model_parameters['max_iterations'] }},
            model_registry='vertex_ai',
            vertex_ai_model_id='fraud_detector',
            vertex_ai_model_version_aliases=['experimental','{{ now().strftime('%Y_%m_%d') }}']
        )
        AS SELECT * FROM tx.feature_table
```

You can notice that the name of the model or the variable for `MAX_ITERATIONS` are parametrised in the SQL query. 
This allows the user to control these parameters directly in the [configuration file](fraud_detector/training/config.yaml) for the training pipeline to reduce duplication of logic. 

```yaml
pipeline_name: power-predictor-training
experiment_name: power-predictor-exp
pipeline_schedule: "1 * * * *"
timezone: "Europe/Berlin"

labels:
  team: team_name

parameters:
  model_name: "tx.fraud_detector"
  model_parameters:
    max_iterations: 20
```

Jinja templating is made possible by creating a custom KFP Component which executes SQL queries. You can find the definition of the component [here](utils/components/bigquery/sql_query.py)

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




