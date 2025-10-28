from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

load_dotenv()

print("🔮 建立塔羅牌資料庫...")

# 簡單的測試資料
data = [
    Document(
        page_content="愚者牌 正位:象徵新的開始、冒險和可能性。今日適合嘗試新事物,保持開放心態。工作上適合開始新專案。感情上單純的心能帶來美好相遇。建議:相信直覺,勇敢踏出第一步!",
        metadata={"card": "愚者", "orientation": "正位"}
    ),
    Document(
        page_content="愚者牌 逆位:代表魯莽和缺乏計劃。今日需要更謹慎評估風險。工作上避免倉促決定。感情上不要被表面吸引。建議:三思而後行,先做好規劃。",
        metadata={"card": "愚者", "orientation": "逆位"}
    ),
    Document(
        page_content="魔術師牌 正位:代表創造力和資源運用。今日你擁有實現目標的一切工具。工作上展現專業能力會得到認可。感情上主動表達用行動證明。建議:善用才能,化想法為現實!",
        metadata={"card": "魔術師", "orientation": "正位"}
    ),
    Document(
        page_content="魔術師牌 逆位:可能代表技能被誤用或缺乏自信。今日需要重新審視能力和目標。工作上避免過度承諾。感情上不要用花言巧語掩飾真心。建議:誠實面對優缺點。",
        metadata={"card": "魔術師", "orientation": "逆位"}
    ),
]

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

print("📚 建立向量資料庫...")
db = FAISS.from_documents(data, embeddings)

print("💾 儲存資料庫...")
db.save_local("faiss_tarot_db")

print("✅ 完成! 資料庫已儲存到 faiss_tarot_db/")
