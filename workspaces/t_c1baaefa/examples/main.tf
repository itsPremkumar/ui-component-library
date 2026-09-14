# Example Terraform configuration with intentional issues for testing

# CRITICAL: Public S3 bucket
resource "aws_s3_bucket" "public_data" {
  bucket = "my-public-data-bucket"
  acl    = "public-read"

  tags = {
    Name = "Public Data"
  }
}

# HIGH: Unencrypted EBS volume
resource "aws_ebs_volume" "data" {
  availability_zone = "us-east-1a"
  size              = 100
  type              = "gp3"
  # encrypted = true  # Missing!
}

# MEDIUM: Oversized EC2 instance
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "m5.4xlarge"

  tags = {
    Name = "web-server"
    Environment = "production"
  }
}

# HIGH: Publicly accessible RDS
resource "aws_db_instance" "main" {
  allocated_storage    = 100
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.m5.xlarge"
  username             = "admin"
  password             = "changeme"
  publicly_accessible  = true
  skip_final_snapshot  = true
}

# MEDIUM: Security group open to world
resource "aws_security_group" "web" {
  name = "web-sg"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# LOW: Missing required tags
resource "aws_sqs_queue" "events" {
  name = "events-queue"
  # No KMS key for encryption
}
