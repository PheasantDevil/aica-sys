# コンテナ化ガイド

Phase 8-2: コンテナ化とオーケストレーション

## 概要

このガイドでは、AICA-SyS をDockerコンテナとして実行し、Kubernetesでオーケストレーションする方法を説明します。

## Docker を使用した実行

### 前提条件

- Docker 20.10以上
- Docker Compose 2.0以上

### 開発環境での実行

```bash
# イメージのビルド
make build

# サービスの起動
make up

# ログの確認
make logs

# サービスの停止
make down
```

### 本番環境での実行

```bash
# 本番イメージのビルド
make prod-build

# 本番環境の起動
make prod-up

# ログの確認
make prod-logs

# 停止
make prod-down
```

## Kubernetes を使用した実行

### 前提条件

- Kubernetes 1.25以上
- kubectl インストール済み
- クラスターへのアクセス権限

### デプロイ手順

#### 1. シークレットの作成

```bash
# シークレットファイルを作成（k8s/secrets.example.yaml をコピー）
cp k8s/secrets.example.yaml k8s/secrets.yaml

# 実際の値を編集
vim k8s/secrets.yaml

# シークレットを適用
kubectl apply -f k8s/secrets.yaml
```

または、コマンドラインから直接作成：

```bash
kubectl create secret generic aica-sys-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=openai-api-key="sk-..." \
  --from-literal=google-ai-api-key="..." \
  --from-literal=stripe-secret-key="sk_..." \
  --from-literal=supabase-url="https://..." \
  --from-literal=supabase-anon-key="..." \
  --from-literal=supabase-service-role-key="..." \
  --from-literal=nextauth-secret="..." \
  --from-literal=nextauth-url="https://aica-sys.com" \
  --from-literal=jwt-secret="..."
```

#### 2. デプロイの実行

```bash
# Makefileを使用（推奨）
make k8s-deploy

# または手動で
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

#### 3. ステータス確認

```bash
# Pods の確認
kubectl get pods -l app=aica-sys

# Services の確認
kubectl get services -l app=aica-sys

# Ingress の確認
kubectl get ingress

# 詳細ステータス
make k8s-status
```

#### 4. ログの確認

```bash
# バックエンドログ
make k8s-logs-backend

# フロントエンドログ
make k8s-logs-frontend

# 特定のPodのログ
kubectl logs -f <pod-name>
```

## イメージのビルドと最適化

### バックエンドイメージ

```bash
# ビルド
docker build -t aica-sys-backend:latest backend/

# サイズ確認
docker images aica-sys-backend

# イメージの詳細
docker inspect aica-sys-backend:latest
```

### フロントエンドイメージ

```bash
# ビルド
docker build -t aica-sys-frontend:latest frontend/

# サイズ確認
docker images aica-sys-frontend

# マルチステージビルドの確認
docker history aica-sys-frontend:latest
```

## スケーリング

### Docker Compose

```bash
# バックエンドを3インスタンスに
docker-compose up -d --scale backend=3

# フロントエンドを2インスタンスに
docker-compose up -d --scale frontend=2
```

### Kubernetes

```bash
# 手動スケーリング
kubectl scale deployment aica-sys-backend --replicas=5

# HPA（水平Pod自動スケーリング）の確認
kubectl get hpa

# HPA の詳細
kubectl describe hpa aica-sys-backend-hpa
```

## トラブルシューティング

### コンテナが起動しない

```bash
# コンテナのステータス確認
docker ps -a

# ログ確認
docker logs <container-id>

# コンテナ内に入る
docker exec -it <container-id> sh
```

### Kubernetes Pod が起動しない

```bash
# Pod のステータス確認
kubectl get pods

# Pod の詳細
kubectl describe pod <pod-name>

# イベント確認
kubectl get events --sort-by=.metadata.creationTimestamp

# Pod 内に入る
kubectl exec -it <pod-name> -- sh
```

### イメージのプル失敗

```bash
# イメージレジストリの認証情報を確認
kubectl get secret regcred

# Secret の作成（必要な場合）
kubectl create secret docker-registry regcred \
  --docker-server=<registry-url> \
  --docker-username=<username> \
  --docker-password=<password>
```

## パフォーマンス最適化

### イメージサイズの削減

1. **マルチステージビルド**: ビルドツールを含めない
2. **Alpine Linux**: 軽量ベースイメージ
3. **.dockerignore**: 不要なファイルを除外
4. **レイヤーキャッシング**: 変更の少ないレイヤーを先に

### リソース制限

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

## セキュリティ

### 非rootユーザー

```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### スキャン

```bash
# Trivyでイメージスキャン
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image aica-sys-backend:latest

# 脆弱性レポート
docker scan aica-sys-backend:latest
```

## 監視とヘルスチェック

### Docker ヘルスチェック

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### Kubernetes プローブ

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

## 便利なコマンド集

### Docker

```bash
# 全コンテナ停止
docker stop $(docker ps -aq)

# 未使用イメージの削除
docker image prune -a

# ボリュームのクリーンアップ
docker volume prune

# システム全体のクリーンアップ
docker system prune -a --volumes
```

### Kubernetes

```bash
# 全リソースの確認
kubectl get all -l app=aica-sys

# リソースの削除
kubectl delete all -l app=aica-sys

# ログのストリーミング
kubectl logs -f -l app=aica-sys --all-containers=true

# Pod の再起動
kubectl rollout restart deployment/aica-sys-backend
```

## 参考資料

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices for Docker](https://docs.docker.com/develop/dev-best-practices/)
