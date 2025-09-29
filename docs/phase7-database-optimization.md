# Phase 7-1: データベース最適化とインデックス設計

## 目的

データベースのパフォーマンスを向上させ、スケーラビリティを確保するための最適化を実施する。

## 現在のデータベース構造分析

### 主要テーブル

1. **users** - ユーザー情報
2. **articles** - 記事コンテンツ
3. **newsletters** - ニュースレター
4. **trends** - トレンド情報
5. **subscriptions** - サブスクリプション
6. **audit_events** - 監査ログ

### 現在のインデックス状況

- プライマリキー: 全テーブルに UUID
- ユニークインデックス: users.email
- 単一インデックス: subscriptions.user_id, audit_events.event_type, audit_events.user_id, audit_events.resource_type, audit_events.timestamp

## 最適化計画

### 1. 複合インデックスの追加

#### articles テーブル

```sql
-- 公開記事の取得（プレミアム記事のフィルタリング）
CREATE INDEX idx_articles_published_premium ON articles(published_at DESC, is_premium);

-- タグ検索の最適化
CREATE INDEX idx_articles_tags_gin ON articles USING GIN(tags);

-- 著者別記事取得
CREATE INDEX idx_articles_author_published ON articles(author, published_at DESC);

-- 人気記事の取得（ビュー数、いいね数）
CREATE INDEX idx_articles_popularity ON articles(views DESC, likes DESC, published_at DESC);
```

#### newsletters テーブル

```sql
-- 公開日順の取得
CREATE INDEX idx_newsletters_published ON newsletters(published_at DESC);

-- 購読者数順の取得
CREATE INDEX idx_newsletters_subscribers ON newsletters(subscribers DESC, published_at DESC);
```

#### trends テーブル

```sql
-- カテゴリ別トレンド取得
CREATE INDEX idx_trends_category_created ON trends(category, created_at DESC);

-- インパクト別トレンド取得
CREATE INDEX idx_trends_impact_created ON trends(impact, created_at DESC);

-- カテゴリとインパクトの複合検索
CREATE INDEX idx_trends_category_impact ON trends(category, impact, created_at DESC);
```

#### subscriptions テーブル

```sql
-- アクティブなサブスクリプション取得
CREATE INDEX idx_subscriptions_user_status ON subscriptions(user_id, status, current_period_end);

-- プラン別サブスクリプション取得
CREATE INDEX idx_subscriptions_plan_status ON subscriptions(plan, status, created_at DESC);

-- 期限切れサブスクリプションの取得
CREATE INDEX idx_subscriptions_expiring ON subscriptions(current_period_end, status);
```

#### audit_events テーブル

```sql
-- ユーザー別監査ログ取得
CREATE INDEX idx_audit_events_user_timestamp ON audit_events(user_id, timestamp DESC);

-- イベントタイプ別監査ログ取得
CREATE INDEX idx_audit_events_type_timestamp ON audit_events(event_type, timestamp DESC);

-- リソース別監査ログ取得
CREATE INDEX idx_audit_events_resource_timestamp ON audit_events(resource_type, resource_id, timestamp DESC);

-- セッション別監査ログ取得
CREATE INDEX idx_audit_events_session_timestamp ON audit_events(session_id, timestamp DESC);

-- 結果別監査ログ取得（エラー分析用）
CREATE INDEX idx_audit_events_result_timestamp ON audit_events(result, timestamp DESC);
```

### 2. 部分インデックスの追加

#### アクティブユーザーのみ

```sql
CREATE INDEX idx_users_active ON users(email) WHERE is_active = true;
```

#### プレミアム記事のみ

```sql
CREATE INDEX idx_articles_premium ON articles(published_at DESC) WHERE is_premium = true;
```

#### アクティブなサブスクリプションのみ

```sql
CREATE INDEX idx_subscriptions_active ON subscriptions(user_id, plan) WHERE status = 'active';
```

### 3. テキスト検索の最適化

#### 記事の全文検索

```sql
-- タイトル検索用
CREATE INDEX idx_articles_title_gin ON articles USING GIN(to_tsvector('english', title));

-- コンテンツ検索用
CREATE INDEX idx_articles_content_gin ON articles USING GIN(to_tsvector('english', content));

-- 要約検索用
CREATE INDEX idx_articles_summary_gin ON articles USING GIN(to_tsvector('english', summary));
```

#### ニュースレターの全文検索

```sql
CREATE INDEX idx_newsletters_title_gin ON newsletters USING GIN(to_tsvector('english', title));
CREATE INDEX idx_newsletters_content_gin ON newsletters USING GIN(to_tsvector('english', content));
```

#### トレンドの全文検索

```sql
CREATE INDEX idx_trends_title_gin ON trends USING GIN(to_tsvector('english', title));
CREATE INDEX idx_trends_description_gin ON trends USING GIN(to_tsvector('english', description));
```

### 4. パーティショニングの検討

#### audit_events テーブルの月次パーティショニング

```sql
-- 月次パーティションの作成
CREATE TABLE audit_events_y2024m01 PARTITION OF audit_events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE audit_events_y2024m02 PARTITION OF audit_events
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- パーティションキーに基づくインデックス
CREATE INDEX idx_audit_events_partition_timestamp ON audit_events(timestamp);
```

### 5. 統計情報の更新設定

```sql
-- 統計情報の自動更新設定
ALTER TABLE articles SET (autovacuum_analyze_scale_factor = 0.1);
ALTER TABLE newsletters SET (autovacuum_analyze_scale_factor = 0.1);
ALTER TABLE trends SET (autovacuum_analyze_scale_factor = 0.1);
ALTER TABLE subscriptions SET (autovacuum_analyze_scale_factor = 0.1);
ALTER TABLE audit_events SET (autovacuum_analyze_scale_factor = 0.05);
```

### 6. 接続プールの最適化

```python
# database.py での接続プール設定
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # 基本接続数
    max_overflow=30,       # 最大追加接続数
    pool_pre_ping=True,    # 接続の健全性チェック
    pool_recycle=3600,     # 接続のリサイクル時間（1時間）
)
```

## 実装手順

1. **インデックス作成スクリプトの作成**
2. **既存データの分析とベンチマーク**
3. **段階的なインデックス追加**
4. **パフォーマンステストの実施**
5. **監視とチューニング**

## 期待される効果

- クエリレスポンス時間の 50%以上短縮
- 同時接続数の向上
- データベースリソース使用量の最適化
- スケーラビリティの向上

## 監視指標

- クエリ実行時間
- インデックス使用率
- 接続プール使用率
- データベースサイズ
- ロック待機時間
