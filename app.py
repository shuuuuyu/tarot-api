from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# ==================== FastAPI 初始化 ====================
app = FastAPI(
    title="Tarot API",
    description="🔮 塔羅牌每日運勢 API",
    version="1.0.0"
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://*.railway.app",  # 新增 Railway 域名
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 全域變數 ====================
qa_chain = None
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ 請設定 GROQ_API_KEY 環境變數!")
if not GEMINI_API_KEY:
    raise ValueError("❌ 請設定 GEMINI_API_KEY 環境變數!")

# ==================== 啟動時載入模型 ====================
@app.on_event("startup")
async def load_models():
    global qa_chain
    print("🔮 正在載入塔羅資料庫...")

    try:
        # 1️⃣ 初始化 Gemini Embeddings
        print("📦 初始化 Gemini Embeddings...")
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GEMINI_API_KEY
        )
        print("✅ Embeddings 初始化完成")

        # 2️⃣ 載入 FAISS 向量資料庫
        print("📚 載入 FAISS 資料庫...")
        db = FAISS.load_local(
            "faiss_tarot_db",
            embeddings,
            allow_dangerous_deserialization=True
        )
        retriever = db.as_retriever(search_kwargs={"k": 3})
        print("✅ FAISS 資料庫載入完成")

        # 3️⃣ 初始化 Groq 模型
        print("🚀 初始化 Groq 模型...")
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=GROQ_API_KEY,
            temperature=0.7
        )
        print("✅ Groq 模型初始化完成")

        # 4️⃣ Prompt 模板
        daily_prompt = ChatPromptTemplate.from_template("""
你是一位專業的塔羅占卜師。根據以下塔羅牌資料,為使用者解讀今日運勢。

塔羅牌資料:
{context}

使用者抽到的牌:{question}

請以溫暖、鼓勵的語氣,用 **繁體中文** 提供:
1. 這張牌對今日的整體運勢建議(2-3 句話)
2. 工作/學業方面的提醒(1-2 句話)
3. 感情/人際方面的提醒(1-2 句話)
4. 一句正向的鼓勵話語

請直接給出解讀,不要加上「根據資料」等前綴。
""")

        # 5️⃣ 建立 QA Chain 函數
        output_parser = StrOutputParser()

        def qa_chain_func(query: str):
            # 檢索相關文件
            docs = retriever.invoke(query)
            context = "\n".join([d.page_content for d in docs])
            
            # 格式化 prompt
            formatted_prompt = daily_prompt.format(context=context, question=query)
            
            # 呼叫 Groq LLM
            response = llm.invoke(formatted_prompt)
            
            return output_parser.invoke(response)

        qa_chain = qa_chain_func
        print("✅ 塔羅資料庫載入完成!")

    except Exception as e:
        print(f"❌ 載入失敗: {e}")
        import traceback
        traceback.print_exc()
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
        "version": "1.0.0",
        "endpoints": {
            "今日運勢": "POST /api/tarot",
            "健康檢查": "GET /health",
            "API 文檔": "GET /docs"
        }
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "model_loaded": qa_chain is not None,
        "groq_api_configured": bool(GROQ_API_KEY),
        "gemini_api_configured": bool(GEMINI_API_KEY)
    }

@app.post("/api/tarot", response_model=TarotResponse)
async def get_daily_fortune(request: TarotRequest):
    """獲取塔羅牌每日運勢"""
    if qa_chain is None:
        raise HTTPException(
            status_code=503,
            detail="模型尚未載入完成,請稍後再試"
        )

    try:
        # 轉換方向為中文
        orientation_zh = "正位" if request.orientation == "upright" else "逆位"
        query = f"{request.card} {orientation_zh}"

        print(f"🔍 收到請求: {query}")
        
        # 調用 QA Chain 生成解讀
        analysis = qa_chain(query)
        
        print(f"✅ 解讀完成")

        return TarotResponse(
            analysis=analysis,
            card=request.card,
            orientation=request.orientation
        )

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成運勢時發生錯誤: {str(e)}"
        )

# ==================== 主程式入口 ====================
if __name__ == "__main__":
    import uvicorn
    # Railway 會提供 PORT 環境變數
    port = int(os.getenv("PORT", 8081))
    uvicorn.run(
        app,
        host="0.0.0.0",  # 重要!必須是 0.0.0.0 才能讓 Railway 訪問
        port=port
    )
