from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    github_token: str = ""
    github_repos: str = ""
    service_urls: str = ""
    guardian_interval_seconds: int = 300
    higgsfield_api_key_id: str = ""
    higgsfield_api_key_secret: str = ""
    allow_automated_repair: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def repositories(self) -> list[str]:
        return [x.strip() for x in self.github_repos.split(",") if x.strip()]

    @property
    def health_urls(self) -> list[str]:
        return [x.strip() for x in self.service_urls.split(",") if x.strip()]

settings = Settings()
