# AICA-SyS API 仕様書

## 概要

AICA-SyS (AI-driven Content Curation & Automated Sales System) のAPI仕様書です。

## ベースURL

- **開発環境**: `http://localhost:3000`
- **本番環境**: `https://aica-sys.com`

## 認証

### NextAuth.js 認証

```typescript
// 認証が必要なエンドポイント
Authorization: Bearer<access_token>;
```

### 認証フロー

1. **Google OAuth ログイン**

   ```http
   GET /api/auth/signin
   ```

2. **セッション取得**

   ```http
   GET /api/auth/session
   ```

3. **ログアウト**
   ```http
   POST /api/auth/signout
   ```

## エンドポイント一覧

### 認証関連

#### ログイン

```http
GET /api/auth/signin
```

#### セッション取得

```http
GET /api/auth/session
```

**レスポンス:**

```json
{
  "user": {
    "id": "string",
    "name": "string",
    "email": "string",
    "image": "string"
  },
  "expires": "string"
}
```

### サブスクリプション管理

#### サブスクリプション情報取得

```http
GET /api/subscription
```

**レスポンス:**

```json
{
  "subscription": {
    "id": "string",
    "status": "active|inactive|cancelled",
    "plan": "free|premium|enterprise",
    "currentPeriodStart": "string",
    "currentPeriodEnd": "string",
    "cancelAtPeriodEnd": "boolean"
  }
}
```

#### 支払い履歴取得

```http
GET /api/subscription/payment-history
```

**レスポンス:**

```json
{
  "payments": [
    {
      "id": "string",
      "amount": "number",
      "currency": "string",
      "status": "succeeded|failed|pending",
      "createdAt": "string"
    }
  ]
}
```

#### 使用量取得

```http
GET /api/subscription/usage
```

**レスポンス:**

```json
{
  "usage": {
    "articlesGenerated": "number",
    "newslettersSent": "number",
    "apiCalls": "number",
    "storageUsed": "number"
  },
  "limits": {
    "maxArticles": "number",
    "maxNewsletters": "number",
    "maxApiCalls": "number",
    "maxStorage": "number"
  }
}
```

### Stripe 決済

#### チェックアウトセッション作成

```http
POST /api/stripe/create-checkout-session
```

**リクエスト:**

```json
{
  "priceId": "string",
  "successUrl": "string",
  "cancelUrl": "string"
}
```

**レスポンス:**

```json
{
  "url": "string"
}
```

#### カスタマーポータルセッション作成

```http
POST /api/stripe/create-portal-session
```

**リクエスト:**

```json
{
  "returnUrl": "string"
}
```

**レスポンス:**

```json
{
  "url": "string"
}
```

#### Webhook

```http
POST /api/stripe/webhook
```

**イベント:**

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

### メール送信

#### メール送信

```http
POST /api/email/send
```

**リクエスト:**

```json
{
  "type": "welcome|newsletter|subscription_confirmation|password_reset",
  "data": {
    "email": "string",
    "name": "string",
    "newsletter": "object",
    "plan": "string",
    "amount": "number",
    "resetLink": "string"
  }
}
```

**レスポンス:**

```json
{
  "success": "boolean",
  "messageId": "string"
}
```

### CSRF 保護

#### CSRF トークン取得

```http
GET /api/csrf/token
```

**レスポンス:**

```json
{
  "token": "string"
}
```

## エラーレスポンス

### 400 Bad Request

```json
{
  "error": "string",
  "message": "string"
}
```

### 401 Unauthorized

```json
{
  "error": "Unauthorized",
  "message": "Authentication required"
}
```

### 403 Forbidden

```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

### 404 Not Found

```json
{
  "error": "Not Found",
  "message": "Resource not found"
}
```

### 429 Too Many Requests

```json
{
  "error": "Rate Limited",
  "message": "Too many requests",
  "retryAfter": "number"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

## レート制限

- **認証済みユーザー**: 1000 requests/hour
- **未認証ユーザー**: 100 requests/hour
- **API エンドポイント**: 100 requests/hour

## セキュリティ

### セキュリティヘッダー

- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- `Content-Security-Policy: default-src 'self'; ...`

### CSRF 保護

すべての状態変更リクエストにはCSRFトークンが必要です。

### 入力値検証

すべての入力値はZodスキーマで検証されます。

## データ型

### 共通型

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  image?: string;
  createdAt: string;
  updatedAt: string;
}

interface Subscription {
  id: string;
  userId: string;
  status: "active" | "inactive" | "cancelled";
  plan: "free" | "premium" | "enterprise";
  currentPeriodStart: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
  createdAt: string;
  updatedAt: string;
}

interface Article {
  id: string;
  title: string;
  content: string;
  description: string;
  author: string;
  tags: string[];
  publishedAt: string;
  updatedAt: string;
  status: "draft" | "published" | "archived";
}

interface Newsletter {
  id: string;
  title: string;
  content: string;
  description: string;
  author: string;
  tags: string[];
  publishedAt: string;
  updatedAt: string;
  status: "draft" | "published" | "archived";
}
```

## 使用例

### 認証フロー

```typescript
// 1. ログイン
const response = await fetch("/api/auth/signin", {
  method: "GET",
});

// 2. セッション取得
const session = await fetch("/api/auth/session", {
  method: "GET",
  headers: {
    Authorization: `Bearer ${accessToken}`,
  },
});

// 3. サブスクリプション情報取得
const subscription = await fetch("/api/subscription", {
  method: "GET",
  headers: {
    Authorization: `Bearer ${accessToken}`,
  },
});
```

### 決済フロー

```typescript
// 1. チェックアウトセッション作成
const checkoutSession = await fetch("/api/stripe/create-checkout-session", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${accessToken}`,
  },
  body: JSON.stringify({
    priceId: "price_1234567890",
    successUrl: "https://aica-sys.com/dashboard?success=true",
    cancelUrl: "https://aica-sys.com/pricing?cancelled=true",
  }),
});

// 2. Stripe Checkout にリダイレクト
const { url } = await checkoutSession.json();
window.location.href = url;
```

### メール送信

```typescript
// ウェルカムメール送信
const emailResponse = await fetch("/api/email/send", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${accessToken}`,
  },
  body: JSON.stringify({
    type: "welcome",
    data: {
      email: "user@example.com",
      name: "John Doe",
    },
  }),
});
```

## 更新履歴

- **v1.0.0** (2024-01-01): 初回リリース
- **v1.1.0** (2024-01-15): メール送信機能追加
- **v1.2.0** (2024-02-01): セキュリティ強化
- **v1.3.0** (2024-02-15): マーケティング機能追加
