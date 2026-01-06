import logging
from django.db import transaction
from .models import ConfiguracaoGlobal
from .schemas import ConfiguracaoGlobalDTO

logger = logging.getLogger(__name__)

class ConfiguracaoGlobalService:
    @staticmethod
    def get_settings_dto() -> ConfiguracaoGlobalDTO:
        config = ConfiguracaoGlobal.load()
        return ConfiguracaoGlobalDTO.from_model(config)

    @staticmethod
    def update_settings(data: dict) -> ConfiguracaoGlobalDTO:
        config = ConfiguracaoGlobal.load()
        with transaction.atomic():
            for field, value in data.items():
                if hasattr(config, field):
                    setattr(config, field, value)
            config.save()
        return ConfiguracaoGlobalDTO.from_model(config)