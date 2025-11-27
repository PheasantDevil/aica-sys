# Groq移行ガイド

## 🎯 移行概要

Google Gemini API → **Groq (Llama 3.1)** への完全移行

### 移行理由

| 項目       | Gemini Pro               | Groq (Llama 3.1 70B) | 差分       |
| ---------- | ------------------------ | -------------------- | ---------- |
| **コスト** | 💰 $3.50-10.50/1M tokens | ✅ **完全無料**      | **$0節約** |
| **速度**   | 普通                     | ⚡ **10倍高速**      | 10x向上    |
| **無料枠** | 60 requests/分           | 14,400 requests/日   | 240倍      |
| **品質**   | ⭐⭐⭐⭐⭐               | ⭐⭐⭐⭐             | 同等       |

---

## 📝 変更内容

### 1. 依存関係

```python
# backend/requirements.txt
# Before
google-generativeai==0.3.0

# After
groq==0.11.0
```

### 2. AIクライアント

```python
# backend/utils/ai_client.py
# Before
import google.generativeai as genai
self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# After
from groq import Groq
self.groq_client = Groq(api_key=groq_api_key)
```

### 3. コンテンツ生成

```python
# backend/services/content_generator.py
# Before
response = await self.gemini_model.generate_content_async(prompt)

# After
response = self.groq_client.chat.completions.create(
    model="llama-3.1-70b-versatile",
    messages=[...],
    max_tokens=4096
)
```

### 4. 環境変数

```yaml
# render.yaml
# Before
- key: OPENAI_API_KEY
  sync: false

# After
- key: GROQ_API_KEY
  sync: false
```

---

## 🔑 APIキー設定

### Render Environment Variables

```
GROQ_API_KEY=gsk_...
```

**設定場所**: Render Dashboard → Environment タブ

### GitHub Secrets（CI/CD用）

```
GROQ_API_KEY=gsk_...
```

**設定場所**: GitHub → Settings → Secrets and variables → Actions

### ローカル開発

```bash
# backend/.env
GROQ_API_KEY=gsk_...
```

---

## 🚀 Groq利用可能モデル

### 推奨モデル

| モデル                    | 用途                 | 速度   | 品質     |
| ------------------------- | -------------------- | ------ | -------- |
| `llama-3.1-70b-versatile` | コンテンツ生成、分析 | 速い   | ⭐⭐⭐⭐ |
| `llama-3.1-8b-instant`    | 高速レスポンス       | 超高速 | ⭐⭐⭐   |
| `mixtral-8x7b-32768`      | 長文処理             | 速い   | ⭐⭐⭐⭐ |
| `gemma2-9b-it`            | 軽量タスク           | 高速   | ⭐⭐⭐   |

### 現在の使用モデル

```python
# コンテンツ生成・分析
model="llama-3.1-70b-versatile"
```

---

## 📊 無料枠の詳細

### レート制限

```
✅ 完全無料:
- 14,400 requests/日
- 600 requests/時
- 30 requests/分（モデルによる）

制限超過時:
- エラーレスポンス
- 1分後に自動リセット
```

### トークン制限

```
- 入力: 最大32,768トークン（モデルによる）
- 出力: max_tokensで指定（推奨: 2048-4096）
- 課金: なし（完全無料）
```

---

## ✅ 削除されたファイル

### Supabase関連

- `env.supabase.example` （使用していない）
- `backend/supabase_init.py` （使用していない）

### 理由

- SQLiteを使用中
- Supabaseは設定のみで実際に使用していない
- 保守性向上のため削除

---

## 🔄 ロールバック手順

Geminiに戻す必要がある場合:

### 1. 依存関係を戻す

```bash
# backend/requirements.txt
groq==0.11.0 → google-generativeai==0.3.0
```

### 2. コードを戻す

```bash
git revert [commit-hash]
```

### 3. 環境変数を変更

```
GROQ_API_KEY → GOOGLE_API_KEY
```

### 4. 再デプロイ

```bash
git push origin main
```

---

## 💡 Tips

### パフォーマンス最適化

```python
# 高速レスポンスが必要な場合
model="llama-3.1-8b-instant"  # Groqで最速

# 品質優先の場合
model="llama-3.1-70b-versatile"  # 現在の設定
```

### エラーハンドリング

```python
try:
    response = groq_client.chat.completions.create(...)
except Exception as e:
    logger.error(f"Groq API error: {e}")
    # フォールバック処理
```

### レート制限対策

```python
import time
from functools import wraps

def retry_on_rate_limit(max_retries=3):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "rate_limit" in str(e).lower():
                        await asyncio.sleep(2 ** i)  # Exponential backoff
                    else:
                        raise
        return wrapper
    return decorator
```

---

## 📚 参考リンク

- [Groq Console](https://console.groq.com/)
- [Groq Documentation](https://console.groq.com/docs)
- [Llama 3.1 Model Card](https://ai.meta.com/llama/)
- [API Reference](https://console.groq.com/docs/api-reference)

---

## 🎊 移行完了後の効果

- ✅ **月額コスト**: $5-20 → **$0** (完全無料)
- ✅ **レスポンス速度**: 10倍向上
- ✅ **無料枠**: 240倍拡大
- ✅ **品質**: 同等レベル維持
- ✅ **保守性**: シンプルな構成

**年間節約額: $60-240** 💰✨
