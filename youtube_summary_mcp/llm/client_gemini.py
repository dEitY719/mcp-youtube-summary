from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from youtube_summary_mcp.llm.gemini_llm_factory import GeminiLLMFactory


load_dotenv()


llm_factory = GeminiLLMFactory()
llm = llm_factory.get_llm()

youtube_url = "https://www.youtube.com/watch?v=HQU2vbsbXkU"
# template 정의
template = "{youtube_url} 영상 요약해줘."

# from_template 메소드를 이용하여 PromptTemplate 객체 생성
prompt = PromptTemplate.from_template(template)

# chain 생성
chain = prompt | llm
result = chain.invoke({"youtube_url": youtube_url})
print(result)