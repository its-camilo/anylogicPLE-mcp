"""AnyLogic Cloud API Client."""

import httpx
from typing import Optional, Dict, Any
import os


class AnyLogicCloudClient:
    """Client for interacting with AnyLogic Cloud API."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANYLOGIC_API_KEY')
        self.base_url = base_url or os.getenv(
            'ANYLOGIC_CLOUD_URL',
            'https://cloud.anylogic.com/api/v1'
        )

        if not self.api_key:
            raise ValueError(
                "AnyLogic API key is required. Set ANYLOGIC_API_KEY environment variable "
                "or pass api_key parameter. Get your key from: "
                "https://cloud.anylogic.com/settings/api-keys"
            )

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                'Authorization': f'Bearer {self.api_key}',
            },
            timeout=60.0
        )

    async def upload_model(
        self,
        model_name: str,
        model_data: bytes,
        enable_source_download: bool = True,
        make_public: bool = False
    ) -> Dict[str, Any]:
        """Upload a model to AnyLogic Cloud."""
        files = {
            'model': (f'{model_name}.alp', model_data, 'application/octet-stream')
        }

        data = {
            'name': model_name,
            'enableSourceDownload': enable_source_download,
            'public': make_public
        }

        response = await self.client.post('/models/upload', files=files, data=data)
        response.raise_for_status()

        return response.json()

    async def get_model(self, model_id: str) -> Dict[str, Any]:
        """Get model information by ID."""
        response = await self.client.get(f'/models/{model_id}')
        response.raise_for_status()
        return response.json()

    async def download_model_source(self, model_id: str) -> bytes:
        """Download model source files (.alp)."""
        response = await self.client.get(f'/models/{model_id}/source')
        response.raise_for_status()
        return response.content

    async def run_simulation(
        self,
        model_id: str,
        experiment_name: str = 'Simulation',
        inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a simulation experiment."""
        payload = {
            'modelId': model_id,
            'experimentName': experiment_name,
            'inputs': inputs or {}
        }

        response = await self.client.post('/simulations/run', json=payload)
        response.raise_for_status()

        return response.json()

    async def get_simulation_results(self, simulation_id: str) -> Dict[str, Any]:
        """Get results from a completed simulation."""
        response = await self.client.get(f'/simulations/{simulation_id}/results')
        response.raise_for_status()
        return response.json()

    async def list_models(self) -> Dict[str, Any]:
        """List all models for the current user."""
        response = await self.client.get('/models')
        response.raise_for_status()
        return response.json()

    async def delete_model(self, model_id: str) -> Dict[str, Any]:
        """Delete a model."""
        response = await self.client.delete(f'/models/{model_id}')
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
