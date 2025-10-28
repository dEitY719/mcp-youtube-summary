import os
from typing import Dict

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr


class GoogleEmbeddingFactory:
    """
    SOLID 원칙과 싱글톤 패턴을 적용한 Google 임베딩 팩토리 클래스.

    동일한 파라미터로 요청 시 기존 임베딩 인스턴스를 재사용합니다.
    """

    _instances: Dict[str, GoogleGenerativeAIEmbeddings] = {}

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

        self._api_key = SecretStr(api_key)

    def get_embedding(
        self, model_name: str = "models/embedding-001"
    ) -> GoogleGenerativeAIEmbeddings:
        """
        지정된 모델명으로 임베딩 인스턴스를 반환합니다.

        Args:
            model_name (str): 사용할 임베딩 모델명.

        Returns:
            GoogleGenerativeAIEmbeddings: 생성되었거나 재사용된 인스턴스.
        """
        if model_name in self._instances:
            return self._instances[model_name]

        embedding = GoogleGenerativeAIEmbeddings(
            model=model_name, google_api_key=self._api_key.get_secret_value()
        )
        self._instances[model_name] = embedding
        return embedding
