-- Enable Row Level Security (RLS) for all public tables
-- Supabase セキュリティ要件対応

-- 1. collection_jobs テーブル
ALTER TABLE public.collection_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow authenticated users to read collection_jobs"
ON public.collection_jobs FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Allow service role full access to collection_jobs"
ON public.collection_jobs FOR ALL
TO service_role
USING (true);

-- 2. analysis_results テーブル
ALTER TABLE public.analysis_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow authenticated users to read analysis_results"
ON public.analysis_results FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Allow service role full access to analysis_results"
ON public.analysis_results FOR ALL
TO service_role
USING (true);

-- 3. articles テーブル
ALTER TABLE public.articles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public to read published articles"
ON public.articles FOR SELECT
TO anon, authenticated
USING (true);

CREATE POLICY "Allow service role full access to articles"
ON public.articles FOR ALL
TO service_role
USING (true);

-- 4. newsletters テーブル
ALTER TABLE public.newsletters ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow authenticated users to read newsletters"
ON public.newsletters FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Allow service role full access to newsletters"
ON public.newsletters FOR ALL
TO service_role
USING (true);

-- 5. trends テーブル
ALTER TABLE public.trends ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public to read trends"
ON public.trends FOR SELECT
TO anon, authenticated
USING (true);

CREATE POLICY "Allow service role full access to trends"
ON public.trends FOR ALL
TO service_role
USING (true);

-- 6. subscriptions テーブル
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own subscriptions"
ON public.subscriptions FOR SELECT
TO authenticated
USING (auth.uid()::text = user_id);

CREATE POLICY "Users can update own subscriptions"
ON public.subscriptions FOR UPDATE
TO authenticated
USING (auth.uid()::text = user_id);

CREATE POLICY "Allow service role full access to subscriptions"
ON public.subscriptions FOR ALL
TO service_role
USING (true);

-- 7. users テーブル
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own data"
ON public.users FOR SELECT
TO authenticated
USING (auth.uid()::text = id);

CREATE POLICY "Users can update own data"
ON public.users FOR UPDATE
TO authenticated
USING (auth.uid()::text = id);

CREATE POLICY "Allow service role full access to users"
ON public.users FOR ALL
TO service_role
USING (true);

-- 8. alembic_version テーブル（マイグレーション管理用）
ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow service role full access to alembic_version"
ON public.alembic_version FOR ALL
TO service_role
USING (true);

-- 9. automated_contents テーブル
ALTER TABLE public.automated_contents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public to read published automated_contents"
ON public.automated_contents FOR SELECT
TO anon, authenticated
USING (status = 'published');

CREATE POLICY "Allow service role full access to automated_contents"
ON public.automated_contents FOR ALL
TO service_role
USING (true);

-- 10. trend_data テーブル
ALTER TABLE public.trend_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public to read trend_data"
ON public.trend_data FOR SELECT
TO anon, authenticated
USING (true);

CREATE POLICY "Allow service role full access to trend_data"
ON public.trend_data FOR ALL
TO service_role
USING (true);

-- 11. source_data テーブル
ALTER TABLE public.source_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow authenticated users to read source_data"
ON public.source_data FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Allow service role full access to source_data"
ON public.source_data FOR ALL
TO service_role
USING (true);

-- 12. content_generation_logs テーブル
ALTER TABLE public.content_generation_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow authenticated users to read content_generation_logs"
ON public.content_generation_logs FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Allow service role full access to content_generation_logs"
ON public.content_generation_logs FOR ALL
TO service_role
USING (true);

-- 確認: すべてのテーブルでRLSが有効化されたことを確認
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM 
    pg_tables
WHERE 
    schemaname = 'public'
ORDER BY 
    tablename;

