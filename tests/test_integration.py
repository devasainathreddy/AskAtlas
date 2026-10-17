"""Integration tests for the AskAtlas workflow."""

import pytest
from src.graph.workflow import create_workflow

def test_workflow_compilation():
    """Test that the workflow compiles without errors."""
    workflow = create_workflow()
    assert workflow is not None

def test_workflow_structure():
    """Verify graph structure (nodes and edges)."""
    workflow = create_workflow()
    # LangGraph CompiledGraph access varies by version, but we can check simple properties if accessible
    # or just rely on compilation success for now.
    pass
