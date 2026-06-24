from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient

from .title_utils import (
    fallback_title,
    is_usable_model_title,
    normalize_title,
)


class TitleUtilsTests(SimpleTestCase):
    def test_normalize_title_removes_prefix_and_punctuation(self):
        self.assertEqual(
            normalize_title('제목: "다이아몬드 채굴법!"', 15),
            "다이아몬드 채굴법",
        )

    def test_fallback_title_removes_request_ending(self):
        self.assertEqual(
            fallback_title("엔더 드래곤 공략 알려주세요!", 15),
            "엔더 드래곤 공략",
        )

    def test_fallback_title_uses_default_for_greeting(self):
        self.assertEqual(fallback_title("ㅎㅇ", 15), "새 채팅")

    def test_fallback_title_converts_question_to_natural_title(self):
        self.assertEqual(
            fallback_title("다이아 어떻게 캐?", 15),
            "다이아 캐는 법",
        )

    def test_model_title_rejects_answer_coordinates(self):
        self.assertFalse(
            is_usable_model_title("다이아몬드는 Y -59", "다이아 어떻게 캐?")
        )


@override_settings(TITLE_MODEL_ID="Qwen/Qwen3.5-0.8B", TITLE_MAX_LENGTH=15)
class TitleApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    @patch("titles.views.title_model_service.generate")
    def test_title_generation(self, generate):
        generate.return_value = "다이아몬드 채굴법"

        response = self.client.post(
            "/api/titles/",
            {
                "question": "다이아는 어떻게 캐?",
                "answer": "Y -59 부근을 탐색하세요.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "다이아몬드 채굴법")
        self.assertEqual(response.json()["source"], "model")

    @patch("titles.views.title_model_service.generate")
    def test_title_generation_uses_fallback(self, generate):
        generate.side_effect = RuntimeError("model unavailable")

        response = self.client.post(
            "/api/titles/",
            {"question": "엔더 드래곤 공략 알려주세요!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "엔더 드래곤 공략")
        self.assertEqual(response.json()["source"], "fallback")

    def test_question_is_required(self):
        response = self.client.post("/api/titles/", {}, format="json")

        self.assertEqual(response.status_code, 400)
