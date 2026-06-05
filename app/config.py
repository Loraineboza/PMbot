from __future__ import annotations

from functools import cached_property
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(..., alias="BOT_TOKEN")
    admin_ids: str = Field(default="", alias="ADMIN_IDS")
    consultant_username: str = Field(default="Elfrida777", alias="CONSULTANT_USERNAME")
    consultant_tg_id: Optional[int] = Field(default=None, alias="CONSULTANT_TG_ID")

    database_path: str = Field(default="data/fitline_pm_bot.sqlite3", alias="DATABASE_PATH")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    throttle_seconds: float = Field(default=0.8, alias="THROTTLE_SECONDS")
    reminder_check_seconds: int = Field(default=3600, alias="REMINDER_CHECK_SECONDS")

    pm_site_url: str = Field(default="https://www.pm-international.com/ru/", alias="PM_SITE_URL")
    pm_products_url: str = Field(
        default="https://www.pm-international.com/ru/ru-ru/about-our-products",
        alias="PM_PRODUCTS_URL",
    )
    fitline_shop_url: str = Field(default="https://www.fitline.com/", alias="FITLINE_SHOP_URL")
    registration_url: str = Field(default="https://www.pmebusiness.com/registrationv2/", alias="REGISTRATION_URL")

    @field_validator("consultant_tg_id", mode="before")
    @classmethod
    def empty_consultant_id_to_none(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        if isinstance(value, str) and value.strip().lower() in {"none", "null", "-"}:
            return None
        if isinstance(value, str) and not value.strip().lstrip("-").isdigit():
            return None
        if value == "":
            return None
        return value

    @cached_property
    def admin_id_list(self) -> list[int]:
        if not self.admin_ids.strip():
            return []
        result: list[int] = []
        for raw_id in self.admin_ids.split(","):
            raw_id = raw_id.strip()
            if raw_id.isdigit():
                result.append(int(raw_id))
        return result

    @property
    def consultant_url(self) -> str:
        return f"https://t.me/{self.consultant_username.lstrip('@')}"


settings = Settings()
