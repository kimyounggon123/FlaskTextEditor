import language_tool_python
from langdetect import detect

from openai import OpenAI


class LanguageDetector:
    def __init__(self):
        pass
    def detect(self, text):
        try:
            return detect(text)
        except:
            return "unknown"
        
# ------------------- 문법 교정 파트 ---------------------
class GrammarManager:
    def __init__(self, type: str = 'en-US'):
        self.tool = language_tool_python.LanguageTool(type)
        self.RULE_KR = {
            # 문장 시작 / 대소문자
            "UPPERCASE_SENTENCE_START": "문장은 대문자로 시작해야 합니다.",
            "LOWERCASE_SENTENCE_START": "문장은 소문자로 시작해야 합니다.",

            # 관사
            "EN_A_VS_AN": "a / an 사용이 잘못되었습니다.",
            "EN_MISSING_ARTICLE": "관사가 빠졌습니다.",
            "EN_UNNECESSARY_ARTICLE": "불필요한 관사가 사용되었습니다.",

            # 주어-동사 / 시제
            "SINGULAR_AGREEMENT_SENT_START": "주어와 동사의 수가 맞지 않습니다.",
            "PERS_PRONOUN_AGREEMENT": "주어(인칭 대명사)와 동사가 일치하지 않습니다.",
            
            "EN_VERB_AGREEMENT": "주어와 동사의 수가 맞지 않습니다.",
            "EN_SIMPLE_PRESENT": "현재형 동사 형태가 잘못되었습니다.",
            "EN_SIMPLE_PAST": "과거형 동사 사용이 잘못되었습니다.",
            "EN_TENSE_CONSISTENCY": "시제가 문맥과 일치하지 않습니다.",

            # 명사 / 품사
            "EN_NOUN_NUMBER": "단수/복수 명사 형태가 잘못되었습니다.",
            "EN_POSSESSIVE": "소유격 사용이 잘못되었습니다.",
            "EN_ADJECTIVE_ADVERB": "형용사 또는 부사 사용이 잘못되었습니다.",

            # 반복 / 부정
            "EN_REDUNDANCY_REPETITION": "불필요한 표현이 반복되었습니다.",
            "EN_DOUBLE_NEGATION": "이중 부정이 사용되었습니다.",

            # 철자
            "MORFOLOGIK_RULE_EN_US": "철자가 잘못되었습니다.",
            "ENGLISH_WORD_REPEAT_RULE": "같은 단어가 반복되었습니다.",

            # 문장부호
            "DOUBLE_PUNCTUATION": "문장 부호가 중복되었습니다.",
            "SPACE_BEFORE_PUNCTUATION": "문장 부호 앞에 공백이 있습니다."
        }

    def check(self, text):
        matches = self.tool.check(text)

        corrected = language_tool_python.utils.correct(text, matches)

        errors = []
        for m in matches:
            original = text[m.offset : m.offset + m.error_length]
            suggestion = m.replacements[0] if m.replacements else ""

            errors.append({
                "code": m.rule_id,
                "message": self.RULE_KR.get(m.rule_id, m.message),
                "original": original,
                "correct": suggestion,
                "offset": m.offset,
                "length": m.error_length
            })

        return corrected, errors


    def fixText(self, text):
        return self.check(text)
    
    
# OpenAI 버전. 해당 과제에서는 사용하지 않음.
class GrammarManagerOpenAI:
    def __init__(self, api_key, model = "gpt-4.1-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def check(self, text, level, language):
        prompt = self.__build_prompt(text, level, language)

        try:
            # 실제 openai에게 메시지 전달 후 응답 대기
            response = self.client.chat.completions.create(
                model = self.model,
                messages = [
                    {"role": "system", "content": "You correct grammar."}, # GPT의 역할을 고정시키는 메시지
                    {"role": "user", "content": prompt} # 실제 user 메시지 (문법 고쳐야 할 문장 전송)
                ]
            )
            # GPT response 구조
            # response - chioce(array) - choice[0] - message - content(GPT 답변 문자열)
            # strip(): 앞뒤 공백 제거 후 개행 제거 함수
            return response.choices[0].message.content.strip() 

        except Exception as e:
            return f"Error: {str(e)}"

    # 실제 openai에게 전달할 문장
    def __build_prompt(self, text, level, language):
        if language == "kr":
            if level == "basic":
                return f"다음 문장의 문법을 고쳐주는데 글의 의미는 바꾸지 말아줘. \n\n {text}"
            else:
                return f"해당 문장을 정확하고 자연스럽게 고쳐줘. \n\n {text}"
        if level == "basic":
            return f"Could you fix the grammar of the following text? you must not change the meaning or rewrite unnecessarily. \n\n {text}"
        else:
            return f"Could you rewrite this naturally? \n\n {text}"
        

