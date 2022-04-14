provider "aws" {
  region = "us-east-1"
}
resource "aws_vpc" "exam_vpc" {
  cidr_block = "101.101.0.0/16"
  tags = {
    Name = "exam_vpc"
  }
}


resource "aws_internet_gateway" "exam_igw" {
  vpc_id = aws_vpc.exam_vpc.id
  tags = {
    Name = "exam_igw"
  }
}
/* Create Public Subnet */
resource "aws_subnet" "public_subnet" {
  vpc_id = aws_vpc.exam_vpc.id
  cidr_block = "101.101.1.0/24"
  map_public_ip_on_launch = "true"
  depends_on = [aws_internet_gateway.exam_igw]
  tags = {
    Name = "public_subnet"
  }
}
/* Create Privet Subnet */
resource "aws_subnet" "privet_subnet" {
  vpc_id = aws_vpc.exam_vpc.id
  cidr_block = "101.101.50.0/24"
  map_public_ip_on_launch = "false"
  tags = {
    Name = "privet_subnet"
  }
}

resource "aws_nat_gateway" "nat_exam" {
  connectivity_type = "private"
  subnet_id = aws_subnet.privet_subnet.id
}