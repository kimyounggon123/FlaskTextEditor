import language_tool_python
from langdetect import detect

from openai import OpenAI


    
# ------------------- 문법 교정 파트 ---------------------
class GrammarManager:
    def __init__(self, type: str = 'en-US'):
        self.tool = language_tool_python.LanguageTool(type)


    def check(self, text):
        matches = self.tool.check(text)
        corrected = language_tool_python.utils.correct(text, matches)

        errors = [] # 틀린 이유 수집
        for m in matches:
            errors.append({
                "rule": m.rule_id,
                "message": m.message,
                "suggestions": m.replacements,
                "offset": m.offset,
                "length": m.error_length,
                "context": m.context
                }
            )

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
        

