import torch
from core.logger import get_logger
from core.settings import EncoderSettings, encoder_settings
from sentence_transformers import SentenceTransformer

logger = get_logger(__name__)


class ModelManager:
    def __init__(self, settings: EncoderSettings):
        self._settings = settings
        self._models = {}
        self._load_model(self._settings.DEFAULT_MODEL_NAME)

    def _load_model(self, model_name):
        if model_name in self._models:
            return self._models[model_name]
        else:
            logger.info(f"Starting to load model '{model_name}'")
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            model = SentenceTransformer(model_name_or_path=model_name,
                                        device=device,
                                        cache_folder=self._settings.LOCAL_MODEL_PATH)
            self._models[model_name] = model
            logger.info(f"Model '{model_name}' loaded successfully")
            return model

    def get_model(self, model_name=None) -> SentenceTransformer:
        if model_name is None or model_name == "":
            model_name = self._settings.DEFAULT_MODEL_NAME

        if model_name not in self._settings.ALLOWED_MODELS:
            error_message = f"Model '{model_name}' is not allowed."
            raise ValueError(error_message)

        if model_name not in self._models:
            self._load_model(model_name)
        return self._models[model_name]
