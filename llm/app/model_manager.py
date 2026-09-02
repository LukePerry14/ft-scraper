import gc
import threading
import time
from typing import Optional

MODEL_NAME = "mlx-community/Qwen3-30B-A3B-Instruct-2507-4bit"
IDLE_TIMEOUT_SECONDS = 5 * 60

class ModelManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self._model = None
        self._tokenizer = None
        self._last_used: Optional[float] = None
        self._lock = threading.Lock()
        self._initialised = True


    def get_model(self):

        with self._lock:
            if self._model is None:
                from mlx_lm import load
                print(f"Loading model ({MODEL_NAME}) into memory...")
                self._model, self._tokenizer = load(MODEL_NAME)
                print("Model loaded.")
            self._last_used = time.time()
            return self._model, self._tokenizer


    def is_loaded(self) -> bool:
        return self._model is not None


    def unload_if_idle(self) -> None:

        with self._lock:
            if self._model is None or self._last_used is None:
                return
            if time.time() - self._last_used < IDLE_TIMEOUT_SECONDS:
                return

            print("Model idle — unloading to free memory...")
            self._model = None
            self._tokenizer = None
            self._last_used = None

            gc.collect()
            try:
                import mlx.core as mx
                mx.clear_cache()
            except Exception:
                pass
