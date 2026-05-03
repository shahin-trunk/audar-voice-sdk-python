"""Voice agent persona management."""

from __future__ import annotations

from typing import Any

import httpx

from audar._http import request_with_retry
from audar.models.voice import (
    PersonaCreateRequest,
    PersonaDetail,
    PersonaListResponse,
    PersonaUpdateRequest,
    PersonaVersionsResponse,
)


class AsyncPersonas:
    """Async persona CRUD operations."""

    def __init__(self, client: httpx.AsyncClient, base_url: str, max_retries: int) -> None:
        self._client = client
        self._base_url = base_url
        self._max_retries = max_retries

    @property
    def _personas_url(self) -> str:
        return f"{self._base_url}/v1/personas"

    async def list(
        self,
        *,
        active_only: bool = True,
        category: str | None = None,
        language: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> PersonaListResponse:
        """List voice agent personas with optional filtering."""
        params: dict[str, Any] = {"active_only": str(active_only).lower(), "skip": skip, "limit": limit}
        if category is not None:
            params["category"] = category
        if language is not None:
            params["language"] = language
        if search is not None:
            params["search"] = search

        resp = await request_with_retry(
            self._client,
            "GET",
            self._personas_url,
            params=params,
            max_retries=self._max_retries,
        )
        return PersonaListResponse.model_validate(resp.json())

    async def get(self, persona_id: str) -> PersonaDetail:
        """Get detailed persona information."""
        resp = await request_with_retry(
            self._client,
            "GET",
            f"{self._personas_url}/{persona_id}",
            max_retries=self._max_retries,
        )
        return PersonaDetail.model_validate(resp.json())

    async def create(self, request: PersonaCreateRequest | dict[str, Any]) -> PersonaDetail:
        """Create a new voice agent persona."""
        if isinstance(request, dict):
            request = PersonaCreateRequest.model_validate(request)

        resp = await request_with_retry(
            self._client,
            "POST",
            self._personas_url,
            json=request.model_dump(exclude_none=True),
            max_retries=self._max_retries,
        )
        return PersonaDetail.model_validate(resp.json())

    async def update(self, persona_id: str, request: PersonaUpdateRequest | dict[str, Any]) -> PersonaDetail:
        """Update an existing persona (partial update)."""
        if isinstance(request, dict):
            request = PersonaUpdateRequest.model_validate(request)

        resp = await request_with_retry(
            self._client,
            "PATCH",
            f"{self._personas_url}/{persona_id}",
            json=request.model_dump(exclude_unset=True),
            max_retries=self._max_retries,
        )
        return PersonaDetail.model_validate(resp.json())

    async def delete(self, persona_id: str) -> None:
        """Delete (deactivate) a persona."""
        await request_with_retry(
            self._client,
            "DELETE",
            f"{self._personas_url}/{persona_id}",
            max_retries=self._max_retries,
        )

    async def set_default(self, persona_id: str) -> PersonaDetail:
        """Set a persona as the default."""
        resp = await request_with_retry(
            self._client,
            "POST",
            f"{self._personas_url}/{persona_id}/set-default",
            max_retries=self._max_retries,
        )
        return PersonaDetail.model_validate(resp.json())

    async def clone(self, persona_id: str, new_name: str) -> PersonaDetail:
        """Clone a persona with a new name."""
        resp = await request_with_retry(
            self._client,
            "POST",
            f"{self._personas_url}/{persona_id}/clone",
            json={"new_name": new_name},
            max_retries=self._max_retries,
        )
        return PersonaDetail.model_validate(resp.json())

    async def versions(
        self, persona_id: str, *, skip: int = 0, limit: int = 10
    ) -> PersonaVersionsResponse:
        """Get version history for a persona."""
        resp = await request_with_retry(
            self._client,
            "GET",
            f"{self._personas_url}/{persona_id}/versions",
            params={"skip": skip, "limit": limit},
            max_retries=self._max_retries,
        )
        return PersonaVersionsResponse.model_validate(resp.json())

    async def restore(self, persona_id: str, version: int) -> PersonaDetail:
        """Restore a persona to a specific version."""
        resp = await request_with_retry(
            self._client,
            "POST",
            f"{self._personas_url}/{persona_id}/restore/{version}",
            max_retries=self._max_retries,
        )
        return PersonaDetail.model_validate(resp.json())
