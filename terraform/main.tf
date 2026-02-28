provider "aws" {
  region = "ap-south-1"
}

resource "aws_instance" "vm" {
  ami           = "ami-0f5ee92e2d63afc18"
  instance_type = "t2.micro"
  key_name      = "your-key"

  vpc_security_group_ids = [aws_security_group.allow_all.id]

  tags = {
    Name = "devops-capstone"
  }
}

resource "aws_security_group" "allow_all" {
  name = "allow_all"

  ingress {
    from_port   = 0
    to_port     = 65535
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