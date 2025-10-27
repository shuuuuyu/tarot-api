from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# ==================== FastAPI 初始化 ====================
app = FastAPI(title="Tarot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 全域變數 ====================
qa_chain = None
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("請設定 GEMINI_API_KEY 環境變數！")

# ==================== 啟動時載入模型 ====================
@app.on_event("startup")
async def load_models():
    global qa_chain
    print("🔮 正在載入塔羅資料庫...")

    try:
        # 1️⃣ Embeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GEMINI_API_KEY
        )

        # 2️⃣ 載入 FAISS 向量資料庫
        db = FAISS.load_local(
            "faiss_tarot_db",
            embeddings,
            allow_dangerous_deserialization=True
        )
        retriever = db.as_retriever(search_kwargs={"k": 3})

        # 3️⃣ 初始化 Gemini 模型
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.7
        )

        # 4️⃣ Prompt 模板
        daily_prompt = ChatPromptTemplate.from_template("""
你是一位專業的塔羅占卜師。根據以下塔羅牌資料，為使用者解讀今日運勢。

塔羅牌資料：
{context}

使用者抽到的牌：{question}

請以溫暖、鼓勵的語氣，用 **繁體中文** 提供：
1. 這張牌對今日的整體運勢建議（2-3 句話）
2. 工作/學業方面的提醒（1-2 句話）
3. 感情/人際方面的提醒（1-2 句話）
4. 一句正向的鼓勵話語

請直接給出解讀，不要加上「根據資料」等前綴。
""")

        # 5️⃣ 手動建立 QA Chain（新版寫法）
        output_parser = StrOutputParser()

        def qa_chain_func(query: str):
            #docs = retriever.get_relevant_documents(query)
            docs = retriever.invoke(query)

            context = "\n".join([d.page_content for d in docs])
            formatted_prompt = daily_prompt.format(context=context, question=query)
            response = llm.invoke(formatted_prompt)
            return output_parser.invoke(response)

        qa_chain = qa_chain_func
        print("✅ 塔羅資料庫載入完成！")

    except Exception as e:
        print(f"❌ 載入失敗：{e}")
        raise

# ==================== API 資料模型 ====================
class TarotRequest(BaseModel):
    card: str
    orientation: str  # upright 或 reversed

class TarotResponse(BaseModel):
    analysis: str
    card: str
    orientation: str

# ==================== API Endpoints ====================
@app.get("/")
async def root():
    return {
        "message": "🔮 塔羅 API 運作中",
        "status": "online",
        "endpoints": {
            "今日運勢": "POST /api/tarot",
            "健康檢查": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": qa_chain is not None}

@app.post("/api/tarot", response_model=TarotResponse)
async def get_daily_fortune(request: TarotRequest):
    if qa_chain is None:
        raise HTTPException(status_code=503, detail="模型尚未載入完成，請稍後再試")

    try:
        orientation_zh = "正位" if request.orientation == "upright" else "逆位"
        query = f"{request.card} {orientation_zh}"

        print(f"📝 收到請求：{query}")
        analysis = qa_chain(query)
        print(f"✅ 解讀完成")

        return TarotResponse(
            analysis=analysis,
            card=request.card,
            orientation=request.orientation
        )

    except Exception as e:
        print(f"❌ 錯誤：{e}")
        raise HTTPException(status_code=500, detail=f"生成運勢時發生錯誤：{str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8081)
