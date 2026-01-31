# Job Intelligence Hub (自動化求職情報中心)

## 專案願景
建立一套全自動化的工作流，定期從各大求職平台（如 104、CakeResume）抓取 Java/後端相關職缺，經由 AI 篩選與摘要後，自動同步至本地 Obsidian Vault。使用者無需手動搜尋，只需專注於筆記閱讀與投遞決策。

## 功能特色
- **多平台爬取**: 支援 104 人力銀行與 CakeResume。
- **AI 智慧分析**: 使用 OpenAI GPT-4o 或 Gemini Pro 清洗資料、提取技術棧並評分匹配度。
- **Obsidian 整合**: 自動生成帶有 YAML Metadata 的 Markdown 檔案。
- **自動化排程**: 定時執行，每日更新。

## 安裝與執行

### 前置需求
- Python 3.10+
- OpenAI API Key 或 Google Gemini API Key
- Obsidian (選用，若需整合筆記)

### 安裝步驟

1. **Clone 專案**
   ```bash
   git clone https://github.com/Cassidy-7749/job-intelligence-hub.git
   cd job-intelligence-hub
   ```

2. **設定環境變數**
   複製 `.env.example` 為 `.env` 並填入 API Key：
   ```bash
   cp .env.example .env
   # 編輯 .env 檔案
   ```

3. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

### 使用方式
```bash
python src/main.py
```
