"""Workflow registry and protocol for downstream-release."""

from downstream_release.workflows.goose import GooseWorkflow
from downstream_release.workflows.protocol import WorkflowProtocol


WORKFLOW_MAP: dict[str, WorkflowProtocol] = {
    "goose": GooseWorkflow(),
}
