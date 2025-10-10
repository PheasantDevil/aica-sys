# Phase 7-3: API レスポンス最適化

## 目的

API のレスポンス時間を短縮し、スループットを向上させるための包括的な最適化を実装する。

## 最適化戦略

### 1. レスポンス時間の短縮

#### 1.1 データベースクエリ最適化

- **N+1 問題の解決**: 一括取得と JOIN の最適化
- **インデックス活用**: 適切なインデックスの設計と使用
- **クエリキャッシュ**: 頻繁に実行されるクエリのキャッシュ化
- **接続プール**: データベース接続の効率的な管理

#### 1.2 データ転送最適化

- **フィールド選択**: 必要なフィールドのみを取得
- **ページネーション**: 効率的なページネーション実装
- **圧縮**: gzip 圧縮の適用
- **ストリーミング**: 大量データのストリーミング配信

#### 1.3 並列処理

- **非同期処理**: async/await の活用
- **並列クエリ**: 複数クエリの並列実行
- **バックグラウンド処理**: 重い処理の非同期化

### 2. レスポンスサイズの最適化

#### 2.1 データ構造最適化

- **フィールドマッピング**: 不要なフィールドの除外
- **ネストレベル削減**: 深いネストの平坦化
- **データ型最適化**: 適切なデータ型の選択

#### 2.2 圧縮とエンコーディング

- **gzip 圧縮**: テキストデータの圧縮
- **JSON 最適化**: 最小限の JSON 構造
- **バイナリデータ**: 適切なバイナリ形式の使用

### 3. キャッシュ戦略の実装

#### 3.1 レスポンスキャッシュ

- **HTTP キャッシュ**: Cache-Control ヘッダーの設定
- **ETag**: 条件付きリクエストの実装
- **Last-Modified**: 最終更新日時の管理

#### 3.2 アプリケーションキャッシュ

- **メモリキャッシュ**: 頻繁にアクセスされるデータのキャッシュ
- **Redis キャッシュ**: 分散キャッシュの実装
- **クエリキャッシュ**: データベースクエリ結果のキャッシュ

### 4. エラーハンドリングの最適化

#### 4.1 エラーレスポンスの最適化

- **統一されたエラーフォーマット**: 一貫性のあるエラー構造
- **適切な HTTP ステータスコード**: 標準的なステータスコードの使用
- **エラーメッセージの最適化**: 簡潔で有用なエラーメッセージ

#### 4.2 エラーログとモニタリング

- **構造化ログ**: 検索可能なログ形式
- **エラー追跡**: エラーの発生パターンの分析
- **アラート**: 重要なエラーの即座な通知

## 実装計画

### 1. パフォーマンスミドルウェアの実装

#### 1.1 レスポンス時間測定

```python
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

#### 1.2 リクエストサイズ制限

```python
@app.middleware("http")
async def request_size_middleware(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        return JSONResponse(
            status_code=413,
            content={"error": "Request too large"}
        )
    return await call_next(request)
```

### 2. データベースクエリ最適化

#### 2.1 一括取得の実装

```python
async def get_articles_optimized(skip: int = 0, limit: int = 10):
    # 一括で記事と関連データを取得
    query = select(Article).options(
        selectinload(Article.tags),
        selectinload(Article.author)
    ).offset(skip).limit(limit)
    return await session.execute(query)
```

#### 2.2 クエリキャッシュの実装

```python
@cache_result(expire=300, key_prefix="articles")
async def get_articles_cached(skip: int = 0, limit: int = 10):
    return await get_articles_optimized(skip, limit)
```

### 3. レスポンス最適化

#### 3.1 フィールド選択の実装

```python
class ArticleResponse(BaseModel):
    id: str
    title: str
    summary: str
    created_at: datetime
    # 不要なフィールドは除外

def optimize_article_response(article: Article) -> ArticleResponse:
    return ArticleResponse(
        id=article.id,
        title=article.title,
        summary=article.summary,
        created_at=article.created_at
    )
```

#### 3.2 ページネーション最適化

```python
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

def create_paginated_response(
    items: List[Any],
    total: int,
    page: int,
    per_page: int
) -> PaginatedResponse:
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        has_next=page * per_page < total,
        has_prev=page > 1
    )
```

### 4. キャッシュヘッダーの設定

#### 4.1 静的リソース

```python
@app.get("/static/{file_path:path}")
async def static_files(file_path: str):
    response = FileResponse(f"static/{file_path}")
    response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return response
```

#### 4.2 API レスポンス

```python
@app.get("/api/articles")
async def get_articles():
    response = JSONResponse(content=articles)
    response.headers["Cache-Control"] = "public, max-age=300, s-maxage=600"
    response.headers["ETag"] = generate_etag(articles)
    return response
```

### 5. 並列処理の実装

#### 5.1 非同期クエリ実行

```python
async def get_dashboard_data():
    # 並列で複数のクエリを実行
    articles_task = get_articles_async()
    trends_task = get_trends_async()
    newsletters_task = get_newsletters_async()

    articles, trends, newsletters = await asyncio.gather(
        articles_task, trends_task, newsletters_task
    )

    return {
        "articles": articles,
        "trends": trends,
        "newsletters": newsletters
    }
```

#### 5.2 バックグラウンド処理

```python
@app.post("/api/articles/generate")
async def generate_article(background_tasks: BackgroundTasks):
    # 重い処理をバックグラウンドで実行
    background_tasks.add_task(generate_article_async, article_data)
    return {"message": "Article generation started"}
```

## 実装手順

1. **パフォーマンスミドルウェアの実装**
2. **データベースクエリ最適化**
3. **レスポンス最適化**
4. **キャッシュヘッダーの設定**
5. **並列処理の実装**
6. **エラーハンドリングの最適化**
7. **パフォーマンステストの実施**

## 期待される効果

- **レスポンス時間**: 60% 以上短縮
- **スループット**: 5 倍以上向上
- **メモリ使用量**: 40% 以上削減
- **エラー率**: 90% 以上削減

## 監視指標

- 平均レスポンス時間
- 95 パーセンタイルレスポンス時間
- スループット（リクエスト/秒）
- エラー率
- メモリ使用量
- CPU 使用率
- データベース接続数
