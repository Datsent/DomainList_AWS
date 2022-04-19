variable "region" {
  description = "Project region"
  default     = "us-east-1"
}
variable "image_url" {
  description = "Image URL on ECR"
  default = "453169210778.dkr.ecr.us-east-1.amazonaws.com/test:latest"
}
variable "dl_cluster" {
  description = "Domain list cluster name"
  default = "dl-cluster"
}
variable "dl_task" {
  description = "Domain list task name"
  default = "dl-task"
}
variable "ecr_repository" {
  description = "Repository name"
  default = "dl_repo_name"
}
