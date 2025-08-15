"""
Tests for the AsyncAgent module.
"""

import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp
import asyncio
from apexai_core.agents.async_agent import AsyncAgent, OllamaAPIError, CodeGenerationError, CodeExecutionError


@pytest.fixture
def async_agent():
    """Create an AsyncAgent instance for testing."""
    return AsyncAgent(
        project_root="test_project",
        max_cycles=2,
        verbose=False,
        ollama_base_url="http://test:11434",
        ollama_model="test-model"
    )


@pytest.mark.asyncio
async def test_ollama_generate_async_success(async_agent):
    """Test that ollama_generate_async successfully generates code."""
    # Mock the aiohttp.ClientSession.post method
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"response": "print('Hello, world!')"})
    
    with patch("aiohttp.ClientSession.post", AsyncMock(return_value=mock_response)):
        code = await async_agent.ollama_generate_async("Test mission")
        
        # Check that the code was generated
        assert "print('Hello, world!')" in code


@pytest.mark.asyncio
async def test_ollama_generate_async_api_error(async_agent):
    """Test that ollama_generate_async raises OllamaAPIError on API error."""
    # Mock the aiohttp.ClientSession.post method to raise an error
    mock_response = MagicMock()
    mock_response.status = 500
    mock_response.text = AsyncMock(return_value="API error")
    
    with patch("aiohttp.ClientSession.post", AsyncMock(return_value=mock_response)):
        with pytest.raises(OllamaAPIError):
            await async_agent.ollama_generate_async("Test mission")


@pytest.mark.asyncio
async def test_write_and_execute_async_success(async_agent):
    """Test that write_and_execute_async successfully writes and executes code."""
    # Mock the aiofiles.open function
    mock_aiofiles = MagicMock()
    mock_aiofiles.__aenter__ = AsyncMock(return_value=mock_aiofiles)
    mock_aiofiles.__aexit__ = AsyncMock(return_value=None)
    mock_aiofiles.write = AsyncMock()
    
    # Mock the _execute_regular_python_async method
    async_agent._execute_regular_python_async = AsyncMock(return_value=(True, "Hello, world!"))
    
    with patch("aiofiles.open", return_value=mock_aiofiles):
        success, output = await async_agent.write_and_execute_async(
            "print('Hello, world!')",
            "test.py"
        )
        
        # Check that the code was executed successfully
        assert success is True
        assert output == "Hello, world!"
        
        # Check that the file was written
        mock_aiofiles.write.assert_called_once_with("print('Hello, world!')")


@pytest.mark.asyncio
async def test_write_and_execute_async_fastapi(async_agent):
    """Test that write_and_execute_async detects and runs FastAPI apps."""
    # Mock the aiofiles.open function
    mock_aiofiles = MagicMock()
    mock_aiofiles.__aenter__ = AsyncMock(return_value=mock_aiofiles)
    mock_aiofiles.__aexit__ = AsyncMock(return_value=None)
    mock_aiofiles.write = AsyncMock()
    
    # Mock the _execute_with_uvicorn_async method
    async_agent._execute_with_uvicorn_async = AsyncMock(return_value=(True, "FastAPI app running"))
    
    # FastAPI code
    fastapi_code = """
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/")
    def read_root():
        return {"Hello": "World"}
    """
    
    with patch("aiofiles.open", return_value=mock_aiofiles):
        success, output = await async_agent.write_and_execute_async(
            fastapi_code,
            "test_fastapi.py"
        )
        
        # Check that the code was executed successfully
        assert success is True
        assert output == "FastAPI app running"
        
        # Check that the FastAPI app was detected
        async_agent._execute_with_uvicorn_async.assert_called_once()


@pytest.mark.asyncio
async def test_auto_install_module_async(async_agent):
    """Test that auto_install_module_async installs missing modules."""
    # Mock the asyncio.create_subprocess_exec function
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.communicate = AsyncMock(return_value=(b"", b""))
    
    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_process)):
        installed_modules = await async_agent.auto_install_module_async(
            "ModuleNotFoundError: No module named 'requests'"
        )
        
        # Check that the module was installed
        assert "requests" in installed_modules


@pytest.mark.asyncio
async def test_recursive_build_async(async_agent):
    """Test that recursive_build_async recursively builds code."""
    # Mock the ollama_generate_async method
    async_agent.ollama_generate_async = AsyncMock(return_value="print('Hello, world!')")
    
    # Mock the write_and_execute_async method
    async_agent.write_and_execute_async = AsyncMock(return_value=(True, "Hello, world!"))
    
    # Mock the operator_review method
    async_agent.operator_review = MagicMock(return_value=True)
    
    # Mock the aiofiles.open function
    mock_aiofiles = MagicMock()
    mock_aiofiles.__aenter__ = AsyncMock(return_value=mock_aiofiles)
    mock_aiofiles.__aexit__ = AsyncMock(return_value=None)
    mock_aiofiles.write = AsyncMock()
    
    with patch("aiofiles.open", return_value=mock_aiofiles):
        await async_agent.recursive_build_async("Test mission")
        
        # Check that ollama_generate_async was called
        async_agent.ollama_generate_async.assert_called_once_with("Test mission", "")
        
        # Check that write_and_execute_async was called
        async_agent.write_and_execute_async.assert_called_once()
        
        # Check that operator_review was called
        async_agent.operator_review.assert_called_once()

