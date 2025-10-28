# tarot-api
# 🔮 塔羅牌每日運勢 API

基於 Groq LLM 和 HuggingFace Embeddings 的塔羅牌占卜 API。

## 快速開始

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

### 2. 設定環境變數
創建 `.env` 檔案:
```
GROQ_API_KEY=你的_Groq_API_Key
```

### 3. 建立塔羅牌資料庫
```bash
python create_db_full_22.py
```

### 4. 啟動 API
```bash
python app.py
```

API 會在 http://localhost:8081 啟動

## 測試 API

### 瀏覽器
訪問 http://localhost:8081/docs 查看 API 文檔並測試

### PowerShell
```powershell
$body = @{card="太陽"; orientation="upright"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8081/api/tarot" -Method Post -Body $body -ContentType "application/json"
```

### Python
```bash
python test_full_output.py
```

## API 端點

- `GET /` - 首頁
- `GET /health` - 健康檢查
- `POST /api/tarot` - 獲取塔羅牌解讀

## 請求範例

```json
{
  "card": "愚者",
  "orientation": "upright"
}
```

orientation 可以是:
- `upright` - 正位
- `reversed` - 逆位

## 支援的塔羅牌

22 張大阿爾克納牌:
愚者、魔術師、女祭司、皇后、皇帝、教皇、戀人、戰車、力量、隱士、命運之輪、正義、倒吊人、死神、節制、惡魔、高塔、星星、月亮、太陽、審判、世界

## 技術架構

- **LLM**: Groq (Llama 3.3 70B)
- **Embeddings**: HuggingFace (Multilingual MiniLM)
- **向量資料庫**: FAISS
- **框架**: FastAPI

## Railway 部署

1. 推送到 GitHub
2. 在 Railway 連接 Repository
3. 設定環境變數 `GROQ_API_KEY`
4. 自動部署

## License

MIT