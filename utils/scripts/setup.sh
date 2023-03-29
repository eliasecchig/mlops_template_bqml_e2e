export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUM=$(gcloud projects list --filter="$PROJECT_ID" --format="value(PROJECT_NUMBER)")
export REGION="us-central1"

# Set required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
      --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com"\
      --role='roles/storage.admin'
gcloud projects add-iam-policy-binding $PROJECT_ID \
      --member="serviceAccount:${PROJECT_NUM}@cloudbuild.gserviceaccount.com"\
      --role='roles/aiplatform.user'
gcloud projects add-iam-policy-binding $PROJECT_ID \
      --member="serviceAccount:${PROJECT_NUM}@cloudbuild.gserviceaccount.com"\
      --role='roles/iam.serviceAccountUser'

# Create pubsub topic and Cloud function to trigger
gcloud pubsub topics create trigger-vertex-pipeline
gcloud functions deploy pipelines-trigger-function \
--source=./utils/tools/cf_pipeline_trigger \
--entry-point=subscribe \
--trigger-topic trigger-vertex-pipeline \
--runtime python37 \
--ingress-settings internal-and-gclb \
--set-env-vars REGION=$REGION,PROJECT_ID=$PROJECT_ID,BUCKET_NAME=$PROJECT_ID-pipelines \
--service-account $PROJECT_NUM-compute@developer.gserviceaccount.com

gsutil mb gs://${PROJECT_ID}-pipelines
gcloud artifacts repositories create pipeline-repository --location=$REGION --repository-format=KFP
