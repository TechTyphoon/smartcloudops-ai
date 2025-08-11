// Private subnets and NAT gateway for production workloads (RDS/ECS)

data "aws_availability_zones" "available_priv" {
  state = "available"
}

resource "aws_eip" "nat_eip" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-nat-eip"
  }
}

resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_subnet_1.id

  tags = {
    Name = "${var.project_name}-nat-gw"
  }
}

resource "aws_subnet" "private_subnet_1" {
  vpc_id            = aws_vpc.smartcloudops_vpc.id
  cidr_block        = var.private_subnet_1_cidr
  availability_zone = data.aws_availability_zones.available_priv.names[0]

  tags = {
    Name = "${var.project_name}-private-subnet-1"
    Type = "Private"
  }
}

resource "aws_subnet" "private_subnet_2" {
  vpc_id            = aws_vpc.smartcloudops_vpc.id
  cidr_block        = var.private_subnet_2_cidr
  availability_zone = data.aws_availability_zones.available_priv.names[1]

  tags = {
    Name = "${var.project_name}-private-subnet-2"
    Type = "Private"
  }
}

resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.smartcloudops_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gw.id
  }

  tags = {
    Name = "${var.project_name}-private-rt"
  }
}

resource "aws_route_table_association" "private_rta_1" {
  subnet_id      = aws_subnet.private_subnet_1.id
  route_table_id = aws_route_table.private_rt.id
}

resource "aws_route_table_association" "private_rta_2" {
  subnet_id      = aws_subnet.private_subnet_2.id
  route_table_id = aws_route_table.private_rt.id
}

