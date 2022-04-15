variable "region" {
  description = "Project region"
  default     = "us-east-1"
}
variable "image_url" {
  description = "Image URL on ECR"
  default = "453169210778.dkr.ecr.us-east-1.amazonaws.com/test:latest"
}