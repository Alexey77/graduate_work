import torch
from core.config import EncoderSettings, encoder_settings
from core.logger import get_logger
from sentence_transformers import SentenceTransformer

logger = get_logger(__name__)


class ModelManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, settings: EncoderSettings):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._settings = settings
        self._models = {}
        self._load_model(self._settings.MODEL_NAME)
        self._initialized = True  # Mark the instance as initialized

    def _load_model(self, model_name):
        if model_name in self._models:
            logger.info(f"Model '{model_name}' is already loaded, retrieving from cache.")
            return self._models[model_name]
        else:
            logger.info(f"Starting to load model '{model_name}'")

            cuda_available = torch.cuda.is_available()
            device = 'cuda' if cuda_available else 'cpu'
            logger.info(f"CUDA available: {cuda_available}. Loading model on '{device}'.")

            model = SentenceTransformer(
                model_name_or_path=model_name,
                device=device,
                cache_folder=self._settings.LOCAL_MODEL_PATH
            )

            self._models[model_name] = model
            logger.info(f"Model '{model_name}' loaded successfully on '{device}'")
            return model

    def get_model(self, model_name=None) -> SentenceTransformer:
        if model_name is None or model_name == "":
            model_name = self._settings.MODEL_NAME

        if model_name not in self._settings.ALLOWED_MODELS:
            error_message = f"Model '{model_name}' is not allowed."
            raise ValueError(error_message)

        if model_name not in self._models:
            self._load_model(model_name)
        return self._models[model_name]
    def unload_models(self):
        logger.info("Unloading all models to free up memory.")
        for model_name, model in self._models.items():
            del model
            logger.info(f"Model '{model_name}' unloaded.")
        self._models.clear()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("Cleared GPU cache.")
