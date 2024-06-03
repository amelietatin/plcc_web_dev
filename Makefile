run_api:
	uvicorn api.main:app --reload --port 8000

bq_reset:
	-bq rm --project_id ${GCP_PROJECT} ${BQ_DATASET}.${TABLE}
	-bq mk --sync --project_id ${GCP_PROJECT} --location=${BQ_REGION} ${BQ_DATASET}.${TABLE}

build:
	docker build . -t api

run:
	docker run -p 8000:${PORT} --env-file .env -t api



# default: pylint pytest

# pylint:
# 	find . -iname "*.py" -not -path "./tests/test_*" | xargs -n1 -I {}  pylint --output-format=colorized {}; true

pytest:
	echo "no tests"

# ----------------------------------
#         LOCAL SET UP
# ----------------------------------

install_requirements:
	@pip install -r requirements.txt

# ----------------------------------
#         HEROKU COMMANDS
# ----------------------------------

streamlit:
	-@streamlit run app.py


# ----------------------------------
#    LOCAL INSTALL COMMANDS
# ----------------------------------
install:
	@pip install . -U

clean:
	@rm -fr */__pycache__
	@rm -fr __init__.py
	@rm -fr build
	@rm -fr dist
	@rm -fr *.dist-info
	@rm -fr *.egg-info
	-@rm model.joblib

# ----------------------------------
#    Deployment COMMANDS
# ----------------------------------
############## register and authorize Gcloud Artifact Registry ############3
gcloud-auth:
	gcloud auth configure-docker ${GCP_REGION}-docker.pkg.dev

gcloud-register-artifact:
	gcloud artifacts repositories create ${GAR_REPO} --repository-format=docker \
	--location=${GCP_REGION} --description="Repository for storing dummy_calculator images"


############# building and pushing to Gcloud Artifact Registry ############3
build-gcloud:
	docker build -t ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${GAR_REPO}/${GAR_IMAGE}:prod .

build-test-gcloud:
	docker run -p 8000:8000 --env-file .env ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${GAR_REPO}/${GAR_IMAGE}:prod

push:
	docker push ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${GAR_REPO}/${GAR_IMAGE}:prod

############# deploy to Google cloud Run #################################3
deploy:
	gcloud run deploy --image ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${GAR_REPO}/${GAR_IMAGE}:prod \
	--memory ${GAR_MEMORY} --region ${GCP_REGION} --env-vars-file .env.yaml --allow-unauthenticated


############ manage Google Cloud Run #####################################3
status:
	gcloud run services list

stop-gcloud:
	gcloud run services delete ${GAR_IMAGE}
