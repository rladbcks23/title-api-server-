from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient

from .title_utils import (
    build_title_prompt,
    fallback_title,
    is_usable_model_title,
    normalize_title,
    usable_answer_for_title,
)


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

    def test_fallback_title_extracts_english_crafting_subject(self):
        self.assertEqual(
            fallback_title("How do I craft an iron pickaxe?", 40),
            "How to Craft an Iron Pickaxe",
        )

    def test_fallback_title_handles_unlisted_how_do_i_question(self):
        self.assertEqual(
            fallback_title("How do I mine diamonds?", 40),
            "How to Mine Diamonds",
        )

    def test_fallback_title_converts_recipe_question(self):
        self.assertEqual(
            fallback_title("What is the recipe of an iron pickaxe?", 40),
            "How to Make an Iron Pickaxe",
        )

    def test_fallback_title_converts_recipe_question_without_article(self):
        self.assertEqual(
            fallback_title("What's the recipe for iron pickaxe?", 40),
            "How to Make Iron Pickaxe",
        )

    def test_model_title_rejects_answer_coordinates(self):
        self.assertFalse(
            is_usable_model_title("Diamonds at Y-59", "How do I mine diamonds?")
        )

    def test_model_title_accepts_how_to_format(self):
        self.assertTrue(
            is_usable_model_title(
                "How to Mine Diamonds",
                "How do I mine diamonds?",
            )
        )

    def test_model_title_rejects_question_format(self):
        self.assertFalse(
            is_usable_model_title(
                "How do I Mine Diamonds",
                "How do I mine diamonds?",
            )
        )

    def test_connection_error_answer_is_ignored(self):
        self.assertEqual(
            usable_answer_for_title("API connection error: timed out"),
            "",
        )
        prompt = build_title_prompt(
            "How do I craft a beacon?",
            "API connection error: timed out",
            15,
        )
        self.assertIn("How do I craft a beacon?", prompt)
        self.assertNotIn("timed out", prompt)


@override_settings(TITLE_MODEL_ID="Qwen/Qwen3.5-4B", TITLE_MAX_LENGTH=40)
class TitleApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertTrue(response.json()["model_enabled"])

    @override_settings(TITLE_MODEL_ENABLED=False)
    @patch("titles.views.title_model_service.generate")
    def test_title_generation_skips_disabled_model(self, generate):
        response = self.client.post(
            "/api/titles/",
            {
                "question": "How do I mine diamonds?",
                "answer": "Search around Y level -59.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["source"], "fallback")
        generate.assert_not_called()

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
        self.assertEqual(response.json()["title"], "redstone farming")
        self.assertEqual(response.json()["source"], "fallback")

    def test_question_is_required(self):
        response = self.client.post("/api/titles/", {}, format="json")

        self.assertEqual(response.status_code, 400)
