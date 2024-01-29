resource "aws_codepipeline" "my_codepipeline" {
    name     = var.codepipeline_name    #CodePipeline 이름
    role_arn = "arn:aws:iam::${var.aws_account_id}:role/service-role/AWS-CodePipeline-Service"  # AWS Account ID

    artifact_store {
        location = var.codepipeline_artifact_store_location     #CodePipeline 아티팩트 저장 S3 버킷 위치
        type     = "S3"
    }

    stage {
        name = "Source"
        action {
            name             = "SourceAction"
            category         = "Source"
            owner            = "AWS"
            provider         = "CodeCommit"
            version          = "1"
            output_artifacts = ["SourceArtifact"]
        }
    }

    stage {
        name = "Build"
        action {
            name             = "BuildAction"
            category         = "Build"
            owner            = "AWS"
            provider         = "CodeBuild"
            version          = "1"
            input_artifacts  = ["SourceArtifact"]
            output_artifacts = ["BuildArtifact"]
            configuration = {
                ProjectName = var.codebuild_project_name      #CodeBuild 프로젝트 이름
            }
        }
    }
    # 필요한 경우 추가 스테이지 및 액션을 여기에 추가합니다.
}
