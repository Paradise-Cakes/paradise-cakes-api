resource "aws_vpc" "paradise_cakes_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name = "pardise-cakes-vpc"
  }
}

resource "aws_subnet" "public_subnet_az1" {
  vpc_id     = aws_vpc.paradise_cakes_vpc.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_subnet" "private_subnet_az1" {
  vpc_id     = aws_vpc.paradise_cakes_vpc.id
  cidr_block = "10.0.2.0/24"
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.paradise_cakes_vpc.id
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.paradise_cakes_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public_rt_association" {
  subnet_id      = aws_subnet.public_subnet_az1.id
  route_table_id = aws_route_table.public_rt.id
}
