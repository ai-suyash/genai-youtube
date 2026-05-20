terraform {
  backend "gcs" {
    bucket = "animated-surfer-496014-h2-terraform-state"
    prefix = "genai-youtube/dev"
  }
}
