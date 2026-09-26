"""Environment-backed settings. Secrets stay in .env, never in git."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    nebius_api_key: str = ""
    nebius_base_url: str = "https://api.tokenfactory.nebius.com/v1/"

    nemotron_fast_model: str = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"
    nemotron_compile_model: str = "nvidia/nemotron-3-super-120b-a12b"
    cosmos_reasoner_model: str = "nvidia/Cosmos3-Super-Reasoner"
    groot_model: str = "nvidia/GR00T-N1.7-3B"

    tavily_api_key: str = ""
    hf_token: str = ""
    hf_user: str = ""

    so101_follower_port: str = "/dev/ttyACM0"
    so101_follower_id: str = "apprentice_follower"
    so101_leader_port: str = "/dev/ttyACM1"
    so101_leader_id: str = "apprentice_leader"
    so101_front_cam: int = 0
    so101_wrist_cam: int = 2
    so101_cam_width: int = 640
    so101_cam_height: int = 480
    so101_cam_fps: int = 30

    skill1_instruction: str = "put the block in the blue bowl"

    request_timeout_s: float = Field(default=120.0, ge=1.0)


def load_settings() -> Settings:
    return Settings()
