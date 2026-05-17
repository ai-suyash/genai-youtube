# Project name used for resource naming
project_name = "adk-production-agent"

# Your Production Google Cloud project id
prod_project_id = "adk-prod-project-496420"

# Your Staging / Test Google Cloud project id
staging_project_id = "adk-staging-project"

# Your Google Cloud project ID that will be used to host the Cloud Build pipelines.
cicd_runner_project_id = "animated-surfer-496014-h2"
# Name of the host connection you created in Cloud Build
host_connection_name = "github-connection"
github_pat_secret_id = "github-token"

repository_owner = "ai-suyash"

# Name of the repository you added to Cloud Build
repository_name = "genai-youtube"

# The Google Cloud region you will use to deploy the infrastructure
region = "us-central1"
