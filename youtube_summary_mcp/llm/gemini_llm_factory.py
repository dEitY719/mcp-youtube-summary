# llm_factory.py
from __future__ import annotations

import os
from typing import Dict

from langchain_core.language_models.llms import BaseLanguageModel
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr


class GeminiLLMFactory:
    """
    SOLID 원칙과 싱글톤 패턴을 적용한 Gemini LLM 팩토리 클래스.

    LLM 인스턴스를 생성하고, 동일한 설정의 인스턴스가 요청되면
    기존에 생성된 인스턴스를 반환하여 리소스를 효율적으로 관리합니다.
    """

    # 팩토리의 싱글톤 인스턴스를 저장하기 위한 딕셔너리
    _instances: Dict[str, BaseLanguageModel] = {}

    # 지원하는 모델 목록
    # 이 목록을 통해 유효성 검사를 수행합니다.
    SUPPORTED_MODELS = {
        "gemini-1.0-pro",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    }

    def __init__(self):
        """
        LLM 팩토리 초기화. 환경 변수에서 API 키를 로드합니다.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

        self._api_key = SecretStr(api_key)

    def get_llm(
        self, model_name: str = "gemini-2.5-flash", temperature: float = 0.5
    ) -> BaseLanguageModel:
        """
        지정된 모델명과 temperature로 LLM 인스턴스를 반환합니다.

        Args:
            model_name (str): 사용할 LLM 모델의 이름.
            temperature (float): LLM의 temperature 값.

        Returns:
            BaseLanguageModel: 생성된 ChatGoogleGenerativeAI 인스턴스.

        Raises:
            ValueError: 지원하지 않는 모델이거나 API 키가 없는 경우.
        """
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"지원하지 않는 모델명입니다: {model_name}. 지원 모델: {self.SUPPORTED_MODELS}"
            )

        # 모델명과 temperature를 결합하여 고유한 키 생성
        instance_key = f"{model_name}-{temperature}"

        # 이미 생성된 인스턴스가 있으면 반환
        if instance_key in self._instances:
            return self._instances[instance_key]

        # 새로운 LLM 인스턴스 생성
        new_llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self._api_key,
            temperature=temperature,
        )

        # 인스턴스를 딕셔너리에 저장
        self._instances[instance_key] = new_llm

        return new_llm
