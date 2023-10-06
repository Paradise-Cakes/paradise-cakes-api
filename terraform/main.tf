terraform {
    backend "s3" {
        bucket = "paradise-cakes-state"
        key    = "remote-state.terraform.tfstate"
        region = "us-east-1"
    }
}