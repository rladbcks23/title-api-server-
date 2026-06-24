from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient

from .title_utils import fallback_title, is_usable_model_title, normalize_title


class TitleUtilsTests(SimpleTestCase):
    def test_normalize_title_removes_prefix_and_punctuation(self):
        self.assertEqual(
            normalize_title('Title: "Mining Diamonds?"', 15),
            "Mining Diamonds",
        )

    def test_fallback_title_removes_request_phrasing(self):
        self.assertEqual(
            fallback_title("Please explain redstone farming.", 15),
            "redstone",
        )

    def test_fallback_title_uses_default_for_greeting(self):
        self.assertEqual(fallback_title("Hello", 15), "New Chat")

    def test_model_title_rejects_answer_coordinates(self):
        self.assertFalse(
            is_usable_model_title("Diamonds at Y-59", "How do I mine diamonds?")
        )


@override_settings(TITLE_MODEL_ID="Qwen/Qwen3.5-4B", TITLE_MAX_LENGTH=15)
class TitleApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    @patch("titles.views.title_model_service.generate")
    def test_title_generation(self, generate):
        generate.return_value = "Mining Diamonds"

        response = self.client.post(
            "/api/titles/",
            {
                "question": "How do I mine diamonds?",
                "answer": "Search around Y level -59.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Mining Diamonds")
        self.assertEqual(response.json()["source"], "model")

    @patch("titles.views.title_model_service.generate")
    def test_title_generation_uses_fallback(self, generate):
        generate.side_effect = RuntimeError("model unavailable")

        response = self.client.post(
            "/api/titles/",
            {"question": "Please explain redstone farming."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "redstone")
        self.assertEqual(response.json()["source"], "fallback")

    def test_question_is_required(self):
        response = self.client.post("/api/titles/", {}, format="json")

        self.assertEqual(response.status_code, 400)
