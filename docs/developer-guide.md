# AICA-SyS 開発者ガイド

## 概要

AICA-SyS (AI-driven Content Curation & Automated Sales System) の開発者向けドキュメントです。システムのアーキテクチャ、開発環境の構築、コントリビューション方法について説明します。

## 目次

1. [システムアーキテクチャ](#システムアーキテクチャ)
2. [開発環境の構築](#開発環境の構築)
3. [プロジェクト構造](#プロジェクト構造)
4. [開発ワークフロー](#開発ワークフロー)
5. [テスト](#テスト)
6. [デプロイメント](#デプロイメント)
7. [API 開発](#api-開発)
8. [データベース設計](#データベース設計)
9. [セキュリティ](#セキュリティ)
10. [パフォーマンス最適化](#パフォーマンス最適化)

## システムアーキテクチャ

### 全体構成

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Services   │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Gemini/OpenAI)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │   GCP Functions │    │   Vector DB     │
│   (Hosting)     │    │   (Processing)  │    │   (Qdrant)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CDN           │    │   Redis Cache   │    │   PostgreSQL    │
│   (Static)      │    │   (Session)     │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 技術スタック

#### Frontend
- **フレームワーク**: Next.js 14 (App Router)
- **言語**: TypeScript
- **スタイリング**: Tailwind CSS
- **UI コンポーネント**: Radix UI
- **状態管理**: TanStack Query
- **認証**: NextAuth.js
- **決済**: Stripe.js
- **テスト**: Jest, React Testing Library, Playwright

#### Backend
- **フレームワーク**: FastAPI
- **言語**: Python 3.11
- **ORM**: SQLAlchemy
- **データベース**: PostgreSQL (本番), SQLite (開発)
- **キャッシュ**: Redis
- **ベクトルDB**: Qdrant
- **AI**: Google AI Studio (Gemini Pro), OpenAI API

#### Infrastructure
- **フロントエンド**: Vercel
- **バックエンド**: GCP Cloud Functions
- **データベース**: PostgreSQL (本番), SQLite (開発)
- **キャッシュ**: Redis
- **ベクトルDB**: Qdrant
- **CDN**: Vercel Edge Network

## 開発環境の構築

### 前提条件

- Node.js 18.19.0+
- Python 3.11+
- Docker & Docker Compose
- Git

### セットアップ手順

#### 1. リポジトリのクローン

```bash
git clone https://github.com/aica-sys/aica-sys.git
cd aica-sys
```

#### 2. 環境変数の設定

```bash
# フロントエンド
cp frontend/.env.example frontend/.env.local

# バックエンド
cp backend/.env.example backend/.env
```

#### 3. 依存関係のインストール

```bash
# フロントエンド
cd frontend
npm install

# バックエンド
cd ../backend
pip install -r requirements.txt
```

#### 4. データベースの起動

```bash
# Docker Composeでサービスを起動
docker-compose up -d postgres redis qdrant
```

#### 5. データベースの初期化

```bash
# バックエンドでデータベースを初期化
cd backend
python -c "from database import init_db; init_db()"
```

#### 6. 開発サーバーの起動

```bash
# フロントエンド (ターミナル1)
cd frontend
npm run dev

# バックエンド (ターミナル2)
cd backend
python main.py
```

### 環境変数

#### フロントエンド (.env.local)

```env
# NextAuth.js
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Resend
RESEND_API_KEY=re_...

# Google Analytics
NEXT_PUBLIC_GA_ID=G-...

# API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### バックエンド (.env)

```env
# データベース
DATABASE_URL=postgresql://user:password@localhost:5432/aica_sys

# Redis
REDIS_URL=redis://localhost:6379

# Qdrant
QDRANT_URL=http://localhost:6333

# AI APIs
GOOGLE_AI_API_KEY=your-google-ai-key
OPENAI_API_KEY=your-openai-key

# GitHub
GITHUB_TOKEN=your-github-token

# その他
SECRET_KEY=your-secret-key
DEBUG=True
```

## プロジェクト構造

```
aica-sys/
├── frontend/                 # Next.js フロントエンド
│   ├── src/
│   │   ├── app/             # App Router ページ
│   │   │   ├── api/         # API ルート
│   │   │   ├── auth/        # 認証ページ
│   │   │   ├── dashboard/   # ダッシュボード
│   │   │   └── ...
│   │   ├── components/      # React コンポーネント
│   │   │   ├── ui/          # UI コンポーネント
│   │   │   └── ...
│   │   ├── lib/             # ユーティリティ
│   │   ├── hooks/           # カスタムフック
│   │   └── types/           # TypeScript 型定義
│   ├── public/              # 静的ファイル
│   ├── prisma/              # Prisma スキーマ
│   └── ...
├── backend/                 # FastAPI バックエンド
│   ├── models/              # データベースモデル
│   ├── api/                 # API エンドポイント
│   ├── services/            # ビジネスロジック
│   ├── utils/               # ユーティリティ
│   └── ...
├── shared/                  # 共有型定義
│   └── types/
├── docs/                    # ドキュメント
├── scripts/                 # スクリプト
└── docker-compose.yml       # Docker Compose 設定
```

## 開発ワークフロー

### Git フロー

1. **feature ブランチの作成**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **開発とコミット**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

3. **プッシュ**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **プルリクエストの作成**
   - GitHub でプルリクエストを作成
   - レビューを依頼

5. **マージ**
   - レビュー承認後、main ブランチにマージ

### コーディング規約

#### TypeScript

```typescript
// インターフェース定義
interface User {
  id: string;
  name: string;
  email: string;
}

// 関数定義
export function getUser(id: string): Promise<User> {
  // 実装
}

// コンポーネント定義
export function UserCard({ user }: { user: User }) {
  return <div>{user.name}</div>;
}
```

#### Python

```python
# 型ヒント
from typing import List, Optional

# データクラス
@dataclass
class User:
    id: str
    name: str
    email: str

# 関数定義
def get_user(user_id: str) -> Optional[User]:
    # 実装
    pass
```

### コミットメッセージ

```
feat: 新機能の追加
fix: バグ修正
docs: ドキュメント更新
style: コードスタイル修正
refactor: リファクタリング
test: テスト追加・修正
chore: その他の変更
```

## テスト

### フロントエンドテスト

#### ユニットテスト (Jest)

```bash
# 全テスト実行
npm run test

# ウォッチモード
npm run test:watch

# カバレッジ
npm run test:coverage
```

#### E2Eテスト (Playwright)

```bash
# E2Eテスト実行
npm run test:e2e

# UIモード
npm run test:e2e:ui
```

### バックエンドテスト

```bash
# テスト実行
pytest

# カバレッジ
pytest --cov=.
```

### テスト戦略

1. **ユニットテスト**: 個別関数・コンポーネントのテスト
2. **統合テスト**: API エンドポイントのテスト
3. **E2Eテスト**: ユーザーフローのテスト
4. **パフォーマンステスト**: 負荷テスト

## デプロイメント

### フロントエンド (Vercel)

1. **Vercel プロジェクトの作成**
2. **GitHub リポジトリの連携**
3. **環境変数の設定**
4. **自動デプロイの設定**

### バックエンド (GCP Cloud Functions)

1. **Cloud Functions の作成**
2. **デプロイスクリプトの実行**
3. **環境変数の設定**
4. **ヘルスチェックの設定**

### データベース (PostgreSQL)

1. **Cloud SQL インスタンスの作成**
2. **データベースの初期化**
3. **接続設定の更新**

## API 開発

### エンドポイント設計

#### RESTful API 原則

- **GET**: リソースの取得
- **POST**: リソースの作成
- **PUT**: リソースの更新
- **DELETE**: リソースの削除

#### エンドポイント例

```python
# 記事一覧取得
@app.get("/api/articles")
async def get_articles(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None
):
    pass

# 記事作成
@app.post("/api/articles")
async def create_article(article: ArticleCreate):
    pass
```

### レスポンス形式

#### 成功レスポンス

```json
{
  "data": {
    "id": "string",
    "title": "string",
    "content": "string"
  },
  "message": "Success"
}
```

#### エラーレスポンス

```json
{
  "error": "string",
  "message": "string",
  "details": {}
}
```

### 認証・認可

#### JWT トークン

```python
# トークン生成
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

#### 認証ミドルウェア

```python
# 認証チェック
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username
```

## データベース設計

### テーブル設計

#### ユーザーテーブル

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 記事テーブル

```sql
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    description TEXT,
    author_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'draft',
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### インデックス設計

```sql
-- パフォーマンス向上のためのインデックス
CREATE INDEX idx_articles_author_id ON articles(author_id);
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_published_at ON articles(published_at);
```

### マイグレーション

```python
# Alembic マイグレーション
def upgrade():
    op.create_table('articles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        # ...
    )

def downgrade():
    op.drop_table('articles')
```

## セキュリティ

### 認証・認可

#### NextAuth.js 設定

```typescript
// next-auth 設定
export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async session({ session, token }) {
      if (token) {
        session.user.id = token.sub!;
      }
      return session;
    },
  },
};
```

#### CSRF 保護

```typescript
// CSRF トークン生成
export function generateCSRFToken(): string {
  return crypto.randomBytes(32).toString('hex');
}

// CSRF トークン検証
export function verifyCSRFToken(token: string, sessionToken: string): boolean {
  return token === sessionToken;
}
```

### 入力値検証

#### Zod スキーマ

```typescript
// 入力値検証スキーマ
export const articleSchema = z.object({
  title: z.string().min(1).max(255),
  content: z.string().min(1),
  description: z.string().optional(),
  tags: z.array(z.string()).optional(),
});

// 検証実行
export function validateArticle(data: unknown) {
  return articleSchema.parse(data);
}
```

### セキュリティヘッダー

```typescript
// セキュリティヘッダー設定
export const securityHeaders = {
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'X-XSS-Protection': '1; mode=block',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
  'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
};
```

## パフォーマンス最適化

### フロントエンド最適化

#### コード分割

```typescript
// 動的インポート
const LazyComponent = dynamic(() => import('./LazyComponent'), {
  loading: () => <Loading />,
  ssr: false,
});
```

#### 画像最適化

```typescript
// Next.js Image コンポーネント
import Image from 'next/image';

export function OptimizedImage({ src, alt }: { src: string; alt: string }) {
  return (
    <Image
      src={src}
      alt={alt}
      width={800}
      height={600}
      priority
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,..."
    />
  );
}
```

#### キャッシュ戦略

```typescript
// TanStack Query キャッシュ
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5分
      cacheTime: 10 * 60 * 1000, // 10分
    },
  },
});
```

### バックエンド最適化

#### データベース最適化

```python
# クエリ最適化
def get_articles_optimized(skip: int, limit: int):
    return db.query(Article)\
        .options(joinedload(Article.author))\
        .offset(skip)\
        .limit(limit)\
        .all()
```

#### キャッシュ実装

```python
# Redis キャッシュ
@cache.memoize(timeout=300)
def get_article(article_id: str):
    return db.query(Article).filter(Article.id == article_id).first()
```

#### 非同期処理

```python
# 非同期処理
async def process_article_async(article_data: dict):
    # 重い処理を非同期で実行
    result = await ai_service.generate_content(article_data)
    return result
```

## 監視・ログ

### ログ設定

```python
# ログ設定
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### メトリクス収集

```typescript
// パフォーマンスメトリクス
export function trackPerformance(metric: string, value: number) {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'timing_complete', {
      name: metric,
      value: value,
    });
  }
}
```

### エラー監視

```typescript
// エラー追跡
export function trackError(error: Error, context?: string) {
  console.error('Error:', error, 'Context:', context);
  
  // エラー監視サービスに送信
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'exception', {
      description: error.message,
      fatal: false,
    });
  }
}
```

## コントリビューション

### コントリビューション手順

1. **Issue の作成**
   - バグ報告や機能要求のIssueを作成
   - ラベルを適切に設定

2. **Fork とブランチ作成**
   ```bash
   git fork https://github.com/aica-sys/aica-sys.git
   git checkout -b feature/your-feature-name
   ```

3. **開発とテスト**
   - 機能を実装
   - テストを追加・実行
   - ドキュメントを更新

4. **プルリクエストの作成**
   - 詳細な説明を記載
   - 関連するIssueをリンク
   - レビューを依頼

### コードレビュー

#### レビューチェックリスト

- [ ] コードが仕様を満たしているか
- [ ] テストが適切に書かれているか
- [ ] パフォーマンスに問題がないか
- [ ] セキュリティに問題がないか
- [ ] ドキュメントが更新されているか

#### レビューコメント

```typescript
// 良い例
// TODO: この関数は将来的に非同期処理に変更予定
export function processData(data: Data[]): ProcessedData[] {
  // 実装
}

// 悪い例
export function processData(data: Data[]): ProcessedData[] {
  // 実装（コメントなし）
}
```

## トラブルシューティング

### よくある問題

#### 開発環境の問題

**問題**: データベースに接続できない
**解決**: Docker Compose のサービスが起動しているか確認

**問題**: 環境変数が読み込まれない
**解決**: .env ファイルの場所と内容を確認

**問題**: 依存関係のインストールに失敗
**解決**: Node.js と Python のバージョンを確認

#### 本番環境の問題

**問題**: デプロイに失敗する
**解決**: 環境変数とビルドログを確認

**問題**: パフォーマンスが悪い
**解決**: データベースクエリとキャッシュ設定を確認

**問題**: エラーが発生する
**解決**: ログとエラー監視ツールを確認

### デバッグ方法

#### フロントエンド

```typescript
// デバッグログ
console.log('Debug:', { data, context });

// エラーハンドリング
try {
  // 処理
} catch (error) {
  console.error('Error:', error);
  // エラー処理
}
```

#### バックエンド

```python
# デバッグログ
import logging
logger = logging.getLogger(__name__)

logger.info(f"Processing data: {data}")

# エラーハンドリング
try:
    # 処理
    pass
except Exception as e:
    logger.error(f"Error occurred: {e}")
    # エラー処理
```

## 更新履歴

- **v1.0.0** (2024-01-01): 初回リリース
- **v1.1.0** (2024-01-15): メール機能追加
- **v1.2.0** (2024-02-01): セキュリティ強化
- **v1.3.0** (2024-02-15): マーケティング機能追加

## サポート

- **開発者向けサポート**: dev-support@aica-sys.com
- **技術的な質問**: GitHub Issues
- **セキュリティ報告**: security@aica-sys.com
- **ドキュメント**: https://docs.aica-sys.com
