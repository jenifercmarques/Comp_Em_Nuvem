from aws_cdk import Stack
from aws_cdk import aws_ecr as ecr
from constructs import Construct


class CloudtaskEcrStack(Stack):
    """Stack de registry ECR da aplicacao (Aula 11)."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ecr.Repository(
            self,
            "CloudtaskApiRepository",
            repository_name="cloudtask-api",
            image_scan_on_push=True,
        )
