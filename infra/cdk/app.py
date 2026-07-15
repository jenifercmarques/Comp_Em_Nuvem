#!/usr/bin/env python3
from __future__ import annotations

import os

import aws_cdk as cdk

from stacks import CloudtaskEcrStack, CloudtaskNetworkStack, CloudtaskStorageStack

app = cdk.App()

account = os.getenv("CDK_DEFAULT_ACCOUNT")
region = os.getenv("CDK_DEFAULT_REGION")
env = cdk.Environment(account=account, region=region)

CloudtaskStorageStack(app, "CloudtaskStorageStack", env=env)
CloudtaskEcrStack(app, "CloudtaskEcrStack", env=env)

# Stack de rede e opcional para evitar custo desnecessario no laboratorio.
if os.getenv("ENABLE_NETWORK_STACK", "false").lower() == "true":
    CloudtaskNetworkStack(app, "CloudtaskNetworkStack", env=env)

app.synth()
