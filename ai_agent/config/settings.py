import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Settings:
    """Configuration settings for the AI Agent system."""
    
    # AI Provider Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Agent Configuration
    AGENT_NAME: str = os.getenv("AGENT_NAME", "AI Assistant")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4096"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Web Interface
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_HOST: str = os.getenv("FLASK_HOST", "localhost")
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///agent_memory.db")
    
    # Tool Configuration
    ENABLE_WEB_SEARCH: bool = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
    ENABLE_FILE_OPERATIONS: bool = os.getenv("ENABLE_FILE_OPERATIONS", "true").lower() == "true"
    ENABLE_CODE_EXECUTION: bool = os.getenv("ENABLE_CODE_EXECUTION", "false").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "60"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "agent.log")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required settings are configured."""
        required_settings = [
            (cls.OPENAI_API_KEY or cls.ANTHROPIC_API_KEY, "At least one AI provider API key must be set"),
        ]
        
        for setting, message in required_settings:
            if not setting:
                print(f"Configuration Error: {message}")
                return False
        
        return True

# Global settings instance
settings = Settings()