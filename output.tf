output "instance_ip_addr" {
  value       = "Open in browser: ${aws_alb.load_balancer.dns_name}"
  description = "Load Balancer DNS name"
}
