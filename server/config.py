from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    model_type: str
    model_name: str
    api_base: str
    api_key: str
    config_name: str
    system_prompt: Optional[str] = None  # 设置为可选，并提供默认值 None
    generate_args: Dict[str, Any] = Field(default={})

