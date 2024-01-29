resource "aws_iam_role" "codebuild_role" {
    name = var.codebuild_role_name      # CodeBuild 역할 이름

    assume_role_policy = jsonencode({
        Version = "2012-10-17",
        Statement = [
            {
                Action = "sts:AssumeRole",
                Effect = "Allow",
                Principal = {
                    Service = "codebuild.amazonaws.com"
                }
            }
        ]
    })
}

resource "aws_iam_policy_attachment" "codebuild_policy" {
    name       = var.codebuild_policy_attachment_name       # CodeBuild 정책 첨부 이름
    policy_arn = "arn:aws:iam::aws:policy/AWSCodeBuildDeveloperAccess"
    roles      = [aws_iam_role.codebuild_role.name]
}

resource "aws_codebuild_project" "my_codebuild_project" {
    name = var.codebuild_project_name       # CodeBuild 프로젝트 이름
    description = var.codebuild_project_description     #CodeBuild 프로젝트 설명
    service_role = aws_iam_role.codebuild_role.arn

    environment {
        compute_type = var.codebuild_compute_type       # CodeBuild 컴퓨팅 유형
        image        = var.codebuild_image      # CodeBuild 이미지
        type         = "LINUX_CONTAINER"
    }

    source {
        type     = "CODEPIPELINE"
        buildspec = var.codebuild_buildspec     # CodeBuild 빌드 스펙 파일
    }

    artifacts {
        type = "CODEPIPELINE"
    }
}
