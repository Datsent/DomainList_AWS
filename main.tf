provider "aws" {
  region = var.region
}

#####################
# Creating cluster  #
#####################
resource "aws_ecs_cluster" "exam_cluster" {
  name = "exam-cluster"
}
/* Setup task */

resource "aws_ecs_task_definition" "exam_task" {
  family                   = "exam-task" # The name of task
  /* Setup container */
  container_definitions    = <<DEFINITION
  [
    {
      "name": "exam-task",

      "image": "${var.image_url}",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 5000,
          "hostPort": 5000
        }
      ],
      "memory": 512,
      "cpu": 256
    }
  ]
  DEFINITION
  requires_compatibilities = ["FARGATE"] # Using ECS Fargate
  network_mode             = "awsvpc"    # Using awsvpc as our network mode as this is required for Fargate
  memory                   = 512         # Setup memory for our container requires
  cpu                      = 256         # Setup CPU for our container requires
  execution_role_arn       = "${aws_iam_role.ecsTaskExecutionRole.arn}"
}

resource "aws_iam_role" "ecsTaskExecutionRole" {
  name               = "ecsTaskExecutionRole"
  assume_role_policy = "${data.aws_iam_policy_document.assume_role_policy.json}"
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ecsTaskExecutionRole_policy" {
  role       = "${aws_iam_role.ecsTaskExecutionRole.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

/* Service */
resource "aws_ecs_service" "exam_service" {
  name            = "exam-service"                             # Name of service
  cluster         = "${aws_ecs_cluster.exam_cluster.id}"             # Link to cluster
  task_definition = "${aws_ecs_task_definition.exam_task.arn}" # link to task
  launch_type     = "FARGATE"
  desired_count   = 2 # Seting number of replicas
  /* Network configuration for service */
  network_configuration {
    subnets          = ["${aws_default_subnet.default_subnet_a.id}", "${aws_default_subnet.default_subnet_b.id}"]
    assign_public_ip = true # Providing our containers with public IPs
    security_groups = ["${aws_security_group.service_security_group.id}"]
  }
  /* Setting load balancer to service */
  load_balancer {
    target_group_arn = "${aws_lb_target_group.target_group.arn}" # Link to target group
    container_name   = "${aws_ecs_task_definition.exam_task.family}"  # Lint to our task
    container_port   = 5000   # Container port
  }
}
/* Security group for service */
resource "aws_security_group" "service_security_group" {
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    security_groups = ["${aws_security_group.load_balancer_security_group.id}"] # Traffic in/from the load balancer security group
  }

  egress {
    from_port   = 0 # Any incoming port
    to_port     = 0 # Any outgoing port
    protocol    = "-1" # Any outgoing protocol
    cidr_blocks = ["0.0.0.0/0"] # All IP addresses
  }
}

# Providing a reference to our default VPC
resource "aws_default_vpc" "default_vpc" {
}

# Providing a reference to our default subnets
resource "aws_default_subnet" "default_subnet_a" {
  availability_zone = "us-east-1a"
}

resource "aws_default_subnet" "default_subnet_b" {
  availability_zone = "us-east-1b"
}
/* Create load balancer */
resource "aws_alb" "load_balancer" {
  name               = "exam-lb"
  load_balancer_type = "application"
  subnets = [ # Link to default subnets
    "${aws_default_subnet.default_subnet_a.id}",
    "${aws_default_subnet.default_subnet_b.id}",
  ]
  # Link to security group
  security_groups = ["${aws_security_group.load_balancer_security_group.id}"]
}

# Creating a security group for the load balancer:
resource "aws_security_group" "load_balancer_security_group" {
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
/* Create target group */
resource "aws_lb_target_group" "target_group" {
  name        = "target-group"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = "${aws_default_vpc.default_vpc.id}" # Link to the default VPC
  health_check {
    matcher = "200,301,302"
    path = "/"
  }
}
/* Create Listeners */
resource "aws_lb_listener" "listener" {
  load_balancer_arn = "${aws_alb.load_balancer.arn}" # Link load balancer
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = "${aws_lb_target_group.target_group.arn}" # Link to our target group
  }
}
output "web_link" {
  value = "Open in browser: ${aws_alb.load_balancer.dns_name}"
}

#####################
# Create CodeBuild  #
#####################

resource "aws_ecr_repository" "ecs_push" {
  name = "ecs_push"
}

resource "aws_codebuild_project" "codebuild_project" {
  name          = "ecr_push"
  description   = "ecr_push"
  build_timeout = "120"
  service_role  = aws_iam_role.codebuild_role.arn
  artifacts {
    type = "NO_ARTIFACTS"
  }

  source {
    type            = "GITHUB"
    location        = "https://github.com/Datsent/ECR_PUSH.git"
    git_clone_depth = 1
    git_submodules_config {
      fetch_submodules = true
    }
  }

  environment {
    image                       = "aws/codebuild/standard:4.0"
    type                        = "LINUX_CONTAINER"
    compute_type                = "BUILD_GENERAL1_SMALL"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true
    environment_variable {
      name  = "DOCKERHUB_USERNAME"
      value = "dockerhub:username"
      type = "SECRETS_MANAGER"
    }
    environment_variable {
      name  = "DOCKERHUB_PASSWORD"
      value = "dockerhub:password"
      type = "SECRETS_MANAGER"
    }
  }

  logs_config {
    cloudwatch_logs {
      group_name  = "log-group"
      stream_name = "log-stream"
    }

    s3_logs {
      status = "DISABLED"
    }
  }
}

# IAM
resource "aws_iam_role" "codebuild_role" {
  name  = "ecr_push_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "codebuild_deploy" {
  role       = aws_iam_role.codebuild_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

