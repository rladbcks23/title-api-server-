from rest_framework import serializers


class TitleRequestSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=4000, trim_whitespace=True)
    answer = serializers.CharField(
        max_length=12000,
        required=False,
        allow_blank=True,
        default="",
    )


class TitleResponseSerializer(serializers.Serializer):
    title = serializers.CharField()
    source = serializers.ChoiceField(choices=("model", "fallback"))
    model = serializers.CharField()

