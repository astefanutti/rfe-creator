"""Shared Anthropic client factory — supports both Vertex AI and direct API."""

import os


def create_client():
    """Create an Anthropic client, auto-detecting Vertex AI or direct API.

    Priority:
    1. Vertex AI if ANTHROPIC_VERTEX_PROJECT_ID is set
    2. Direct API if ANTHROPIC_API_KEY is set
    3. Raise error
    """
    project_id = os.environ.get("ANTHROPIC_VERTEX_PROJECT_ID")
    region = os.environ.get("CLOUD_ML_REGION", "us-east5")

    if project_id:
        from anthropic import AnthropicVertex
        return AnthropicVertex(project_id=project_id, region=region)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        from anthropic import Anthropic
        return Anthropic(api_key=api_key)

    raise RuntimeError(
        "No Anthropic auth found. Set ANTHROPIC_VERTEX_PROJECT_ID (for Vertex AI) "
        "or ANTHROPIC_API_KEY (for direct API)."
    )
