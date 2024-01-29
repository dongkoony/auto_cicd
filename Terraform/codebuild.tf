# Code Build IAM Role & Project ADD

resource "aws_iam_role" "codebuild_role" {
    name = "codebuild-role"

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
    name       = "codebuild-policy-attachment"  # 'name' 인자 추가
    policy_arn = "arn:aws:iam::aws:policy/AWSCodeBuildDeveloperAccess"
    roles      = [aws_iam_role.codebuild_role.name]  # 'role' 대신 'roles' 사용
}


resource "aws_codebuild_project" "my_codebuild_project" {
    name = "my-codebuild-project"
    description = "My CodeBuild Project"
    service_role = aws_iam_role.codebuild_role.arn

    environment {
        compute_type = "BUILD_GENERAL1_SMALL"
        image = "aws/codebuild/standard:4.0"
        type = "LINUX_CONTAINER"
    }

    source {
        type = "CODEPIPELINE"
        buildspec = "buildspec.yaml"
    }

    artifacts {
        type = "CODEPIPELINE"
    }
}