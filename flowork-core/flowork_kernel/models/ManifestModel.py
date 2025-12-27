########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\models\ManifestModel.py
########################################################################

from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Dict, Optional, Any, Union

# [ADDED] Standard Android-based categories for Flowork ecosystem
VALID_CATEGORIES = [
    "productivity",
    "tools",
    "utilities",
    "communication",
    "developer_tools",
    "artificial_intelligence",
    "education",
    "finance",
    "business",
    "media_graphics",
    "social",
    "lifestyle"
]

# [ADDED] Standard Capability Flags for Hybrid Apps
VALID_CAPABILITIES = ["online", "offline", "hybrid"]

class GuiInputOption(BaseModel):
    label: str
    value: Any

class GuiInput(BaseModel):
    name: str = Field(..., description="Internal variable name sent to backend")
    type: str = Field(..., description="Type: text, number, boolean, select, file, code, cron, secret")
    label: str = Field(..., description="Human readable label")
    default: Optional[Any] = None
    placeholder: Optional[str] = None
    required: bool = False
    description: Optional[str] = None
    options: Optional[Union[List[str], List[GuiInputOption]]] = None
    hidden: bool = False
    @validator('options', pre=True)
    def parse_options(cls, v):
        if isinstance(v, list) and v and isinstance(v[0], str): return [{"label": x, "value": x} for x in v]
        return v

class NodePort(BaseModel):
    name: str
    type: str = "any"
    label: Optional[str] = None

class AppNode(BaseModel):
    id: str = Field(..., description="Unique Node ID within the App")
    label: Optional[str] = None
    name: Optional[str] = None
    type: str = Field("action", description="trigger | action")
    icon: Optional[str] = "mdi-puzzle"
    description: str = "No description provided"
    category: str = "general"
    inputs: List[GuiInput] = []
    input_ports: List[NodePort] = []
    output_ports: List[NodePort] = []
    python_handler: str = "execute"
    # [ADDED] Logic for Hybrid Nodes (Online JS vs Offline Python)
    # If handler is 'js_callback', the node runs in frontend only
    handler_type: str = Field("python", description="python | javascript")

    @root_validator(pre=True)
    def fill_label_name(cls, values):
        if 'label' not in values and 'name' in values: values['label'] = values['name']
        if 'name' not in values and 'label' in values: values['name'] = values['label']
        return values

class AppGuiConfig(BaseModel):
    dashboard_enabled: bool = False
    dashboard_path: str = "index.html"
    icon: str = "icon.svg"
    settings: List[GuiInput] = []
    # [ADDED] Flag for standalone apps (Games, Managers)
    is_standalone: bool = False

class ManifestModel(BaseModel):
    id: str = Field(..., pattern=r"^[a-z0-9_]+$", description="App ID")
    name: str
    version: str = "1.0.0"
    author: str = "Unknown"
    description: str
    category: str = "utilities"

    icon: str = "icon.svg"

    tier: Optional[str] = "architect"

    nodes: List[AppNode] = []
    gui: AppGuiConfig = Field(default_factory=AppGuiConfig)
    requires_services: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    is_paused: Optional[bool] = False

    # [ADDED] Hybrid capability definition
    # online: cloudflare only, offline: local engine only, hybrid: both
    capability: str = Field("offline", description="online | offline | hybrid")

    @validator('category')
    def validate_category(cls, v):
        v = v.lower().replace(" ", "_")
        if v not in VALID_CATEGORIES:
            return "utilities"
        return v

    # [ADDED] Validator for capability
    @validator('capability')
    def validate_capability(cls, v):
        if v not in VALID_CAPABILITIES:
            return "offline"
        return v

    class Config: extra = "ignore"