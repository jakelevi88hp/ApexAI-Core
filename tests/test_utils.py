"""
Tests for the utils module.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from apexai_core.utils import (
    check_ollama_availability,
    list_available_models,
    run_command,
    install_package,
    is_fastapi_code,
    create_file,
)


def test_is_fastapi_code():
    """Test that is_fastapi_code correctly identifies FastAPI code."""
    # FastAPI code
    fastapi_code = """
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/")
    def read_root():
        return {"Hello": "World"}
    """
    
    # Regular Python code
    regular_code = """
    def hello_world():
        return "Hello, World!"
    
    if __name__ == "__main__":
        print(hello_world())
    """
    
    assert is_fastapi_code(fastapi_code) is True
    assert is_fastapi_code(regular_code) is False


def test_create_file(tmp_path):
    """Test that create_file creates a file with the specified content."""
    # Create a temporary file
    file_path = tmp_path / "test.txt"
    content = "Hello, World!"
    
    # Create the file
    result = create_file(str(file_path), content)
    
    # Check that the file was created
    assert result is True
    assert file_path.exists()
    
    # Check that the file contains the expected content
    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == content


def test_create_file_with_directory(tmp_path):
    """Test that create_file creates directories if they don't exist."""
    # Create a temporary file in a subdirectory
    file_path = tmp_path / "subdir" / "test.txt"
    content = "Hello, World!"
    
    # Create the file
    result = create_file(str(file_path), content)
    
    # Check that the file was created
    assert result is True
    assert file_path.exists()
    
    # Check that the file contains the expected content
    with open(file_path, "r", encoding="utf-8") as f:
        assert f.read() == content


@patch("subprocess.run")
def test_run_command_success(mock_run):
    """Test that run_command returns success and output for successful commands."""
    # Mock subprocess.run to return success
    mock_process = MagicMock()
    mock_process.stdout = "Command output"
    mock_run.return_value = mock_process
    
    # Run the command
    success, output = run_command(["echo", "Hello, World!"])
    
    # Check that the command was successful
    assert success is True
    assert output == "Command output"
    
    # Check that subprocess.run was called with the expected arguments
    mock_run.assert_called_once_with(
        ["echo", "Hello, World!"],
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=None
    )


@patch("subprocess.run")
def test_run_command_failure(mock_run):
    """Test that run_command returns failure and error output for failed commands."""
    # Mock subprocess.run to raise CalledProcessError
    mock_error = MagicMock()
    mock_error.stderr = "Command failed"
    mock_run.side_effect = [
        pytest.raises(Exception),
        mock_error
    ]
    
    # Run the command
    success, output = run_command(["nonexistent_command"])
    
    # Check that the command failed
    assert success is False
    assert output == "Command failed"

