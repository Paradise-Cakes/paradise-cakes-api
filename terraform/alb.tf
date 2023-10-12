resource "aws_lb" "paradise_cakes_lb" {
  name               = "paradise-cakes-lb"
  internal           = false
  load_balancer_type = "application"
  subnets            = [aws_subnet.public_subnet_az1.id]
}

resource "aws_lb_target_group" "paradise_cakes_target_group" {
  name     = "paradise-cakes-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_subnet.public_subnet_az1.vpc_id
}
