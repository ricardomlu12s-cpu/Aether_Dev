from __future__ import annotations

from fastapi import APIRouter, Depends

from ..auth import require_admin
from ..services.audit_service import audit
from ..services.plugin_runtime import plugin_runtime

router = APIRouter()


@router.get("/plugins")
def list_plugins() -> list[dict]:
    return plugin_runtime.list_plugins()


@router.post("/plugins/{name}/enable")
def enable_plugin(name: str, actor: str = Depends(require_admin)) -> dict:
    audit(actor, "plugin.enable", "plugin", name)
    return plugin_runtime.set_enabled(name, True)


@router.post("/plugins/{name}/disable")
def disable_plugin(name: str, actor: str = Depends(require_admin)) -> dict:
    audit(actor, "plugin.disable", "plugin", name)
    return plugin_runtime.set_enabled(name, False)

