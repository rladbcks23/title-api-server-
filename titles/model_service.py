import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from django.conf import settings

from .title_utils import build_title_prompt, normalize_title


class TitleModelService:
    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._load_lock = threading.Lock()
        self._generation_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=1)

    @property
    def loaded(self):
        return self._model is not None and self._tokenizer is not None

    def load(self):
        if self.loaded:
            return

        with self._load_lock:
            if self.loaded:
                return

            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(
                settings.TITLE_MODEL_ID,
                trust_remote_code=True,
            )
            model_kwargs = {
                "trust_remote_code": True,
                "device_map": settings.TITLE_MODEL_DEVICE,
                "torch_dtype": "auto",
            }
            if settings.TITLE_MODEL_DTYPE != "auto":
                model_kwargs["torch_dtype"] = getattr(
                    torch,
                    settings.TITLE_MODEL_DTYPE,
                )

            model = AutoModelForCausalLM.from_pretrained(
                settings.TITLE_MODEL_ID,
                **model_kwargs,
            )
            model.eval()

            self._tokenizer = tokenizer
            self._model = model

    def generate(self, question: str, answer: str) -> str:
        future = self._executor.submit(self._generate_sync, question, answer)
        try:
            return future.result(timeout=settings.TITLE_MODEL_TIMEOUT_SECONDS)
        except TimeoutError as exc:
            future.cancel()
            raise RuntimeError("Title generation timed out") from exc

    def _generate_sync(self, question: str, answer: str) -> str:
        self.load()

        import torch

        prompt = build_title_prompt(
            question=question,
            answer=answer,
            max_length=settings.TITLE_MAX_LENGTH,
        )
        messages = [{"role": "user", "content": prompt}]
        template_kwargs = {
            "tokenize": False,
            "add_generation_prompt": True,
        }
        try:
            rendered_prompt = self._tokenizer.apply_chat_template(
                messages,
                enable_thinking=False,
                **template_kwargs,
            )
        except TypeError:
            rendered_prompt = self._tokenizer.apply_chat_template(
                messages,
                **template_kwargs,
            )

        inputs = self._tokenizer(rendered_prompt, return_tensors="pt")
        model_device = next(self._model.parameters()).device
        inputs = {key: value.to(model_device) for key, value in inputs.items()}

        generation_kwargs = {
            **inputs,
            "max_new_tokens": settings.TITLE_MODEL_MAX_NEW_TOKENS,
            "do_sample": settings.TITLE_MODEL_TEMPERATURE > 0,
            "pad_token_id": self._tokenizer.eos_token_id,
        }
        if settings.TITLE_MODEL_TEMPERATURE > 0:
            generation_kwargs["temperature"] = settings.TITLE_MODEL_TEMPERATURE

        with self._generation_lock, torch.inference_mode():
            output = self._model.generate(**generation_kwargs)

        generated_tokens = output[0, inputs["input_ids"].shape[1] :]
        generated_text = self._tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True,
        )
        title = normalize_title(generated_text, settings.TITLE_MAX_LENGTH)
        if not title:
            raise RuntimeError("Model returned an empty title")
        return title


title_model_service = TitleModelService()

