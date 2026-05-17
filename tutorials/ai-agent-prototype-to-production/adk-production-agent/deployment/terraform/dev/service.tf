# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Wait for IAM bindings to propagate before creating Agent Engine resource
# IAM changes can take 60-120 seconds to propagate in Google Cloud
resource "time_sleep" "wait_for_iam_propagation" {
  create_duration = "120s"

  depends_on = [
    google_project_iam_member.app_sa_roles,
    google_project_iam_member.vertex_ai_sa_permissions,
  ]
}

resource "google_vertex_ai_reasoning_engine" "app" {
  provider = google-beta
  display_name = var.project_name
  description  = "Agent deployed via Terraform"
  region       = var.region
  project      = var.dev_project_id

  spec {
    agent_framework = "google-adk"
    service_account = google_service_account.app_sa.email

    deployment_spec {
      min_instances         = 1
      max_instances         = 10
      container_concurrency = 9

      resource_limits = {
        cpu    = "4"
        memory = "8Gi"
      }

      env {
        name  = "LOGS_BUCKET_NAME"
        value = google_storage_bucket.logs_data_bucket.name
      }

      env {
        name  = "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
        value = "true"
      }

      env {
        name  = "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"
        value = "true"
      }
    }

    source_code_spec {
      inline_source {
        source_archive = filebase64("${path.module}/../fixtures/dummy-source.tar.gz")
      }

      python_spec {
        entrypoint_module  = "app.agent_engine_app"
        entrypoint_object  = "agent_engine"
        requirements_file  = "app/app_utils/.requirements.txt"
        version            = "3.12"
      }
    }
  }

  timeouts {
    create = "30m"
    update = "30m"
    delete = "30m"
  }

  # This lifecycle block prevents Terraform from overwriting the source code when it's
  # updated by Agent Engine deployments outside of Terraform (e.g., via CI/CD pipelines)
  lifecycle {
    ignore_changes = [
      spec[0].source_code_spec,
    ]
  }

  # Ensure APIs, service account, IAM bindings, and storage are all ready
  # before creating the Agent Engine resource
  depends_on = [
    google_project_service.services,
    google_project_iam_member.app_sa_roles,
    google_project_iam_member.vertex_ai_sa_permissions,
    google_storage_bucket.logs_data_bucket,
    time_sleep.wait_for_iam_propagation,
  ]
}
