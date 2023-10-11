resource "aws_elb" "main" {
  name               = "paradise-cakes-elb"
  availability_zones = ["us-east-1"]

  listener {
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }
}
