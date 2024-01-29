resource "aws_instance" "ubuntu_instance" {
    ami           = var.ami_id
    instance_type = var.instance_type
    key_name      = var.key_name

    root_block_device {
        volume_size = var.root_volume_size
    }

    tags = {
    Name = "App_Server"
    }
}
