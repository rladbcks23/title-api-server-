from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .model_service import title_model_service
from .serializers import TitleRequestSerializer, TitleResponseSerializer
from .title_utils import fallback_title, is_usable_model_title


class HealthView(APIView):
    def get(self, request):
        return Response(
            {
                "status": "ok",
                "model_enabled": settings.TITLE_MODEL_ENABLED,
                "model": settings.TITLE_MODEL_ID,
                "loaded": title_model_service.loaded,
            }
        )


class TitleCreateView(APIView):
    def post(self, request):
        request_serializer = TitleRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        question = request_serializer.validated_data["question"]
        answer = request_serializer.validated_data["answer"]

        if not settings.TITLE_MODEL_ENABLED:
            title = fallback_title(question, settings.TITLE_MAX_LENGTH)
            source = "fallback"
        else:
            try:
                title = title_model_service.generate(question, answer)
                if not is_usable_model_title(title, question):
                    raise ValueError("Model returned an unsuitable title")
                source = "model"
            except Exception:
                title = fallback_title(question, settings.TITLE_MAX_LENGTH)
                source = "fallback"

        response_serializer = TitleResponseSerializer(
            {
                "title": title,
                "source": source,
                "model": settings.TITLE_MODEL_ID,
            }
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)
