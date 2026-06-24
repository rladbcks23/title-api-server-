import re


DEFAULT_TITLE = "새 채팅"
QUESTION_PATTERNS = (
    (r"^(.+?)\s+어떻게\s+캐(?:요|나요|지|야)?$", r"\1 캐는 법"),
    (r"^(.+?)\s+어떻게\s+가(?:요|나요|지|야)?$", r"\1 가는 법"),
    (r"^(.+?)\s+만들(?:어|어요|지|까)?$", r"\1 만드는 법"),
    (r"^(.+?)\s+어떻게\s+얻(?:어|어요|지|나요)?$", r"\1 얻는 법"),
    (r"^(.+?)\s+어떻게\s+찾(?:아|아요|지|나요)?$", r"\1 찾는 법"),
    (r"^(.+?)\s+어떻게\s+잡(?:아|아요|지|나요)?$", r"\1 잡는 법"),
)


def build_title_prompt(question: str, answer: str, max_length: int) -> str:
    return f"""다음 대화의 채팅방 제목만 작성하세요.

규칙:
- 한국어 명사형
- {max_length}자 이내
- 질문의 핵심 주제를 중심으로 표현
- 답변은 질문의 의미를 보완할 때만 참고
- 좌표, 버전, 수치 등 세부 답변 내용은 제목에서 제외
- 문장부호, 따옴표, 접두사, 설명 금지
- 제목 한 줄만 출력

질문:
{question[:2000]}

답변:
{answer[:4000]}
"""


def normalize_title(value: str, max_length: int) -> str:
    title = value.strip().splitlines()[0] if value.strip() else ""
    title = re.sub(r"^(?:제목|title)\s*:\s*", "", title, flags=re.IGNORECASE)
    title = title.strip("\"'`“”‘’[](){}")
    title = re.sub(r"[?!.,。！？]+$", "", title).strip()
    title = " ".join(title.split())

    if not title:
        return ""
    if len(title) <= max_length:
        return title

    shortened = title[:max_length].rstrip()
    if " " in shortened:
        shortened = shortened.rsplit(" ", 1)[0]
    return shortened or title[:max_length]


def fallback_title(question: str, max_length: int) -> str:
    title = " ".join(question.split()).strip()
    title = re.sub(r"[?!.,。！？]+", "", title).strip()

    for pattern, replacement in QUESTION_PATTERNS:
        if re.fullmatch(pattern, title):
            title = re.sub(pattern, replacement, title)
            break

    title = re.sub(
        r"\s*(?:알려\s*줘|알려\s*주세요|설명해\s*줘|설명해\s*주세요)$",
        "",
        title,
    ).strip()

    if title.casefold() in {"hi", "hello", "ㅎㅇ", "안녕", "안녕하세요"}:
        return DEFAULT_TITLE
    return normalize_title(title, max_length) or DEFAULT_TITLE


def is_usable_model_title(title: str, question: str) -> bool:
    normalized_question = normalize_title(question, len(question))
    if not title or title == normalized_question:
        return False
    if re.search(r"\d", title):
        return False
    if re.search(r"(?:어떻게|왜|뭐|무엇|어디|언제)", title):
        return False
    return True
