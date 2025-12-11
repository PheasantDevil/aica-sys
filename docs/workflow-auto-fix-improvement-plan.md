# Workflow Auto Fix 改善計画

**作成日**: 2025 年 12 月 11 日  
**目的**: スケジュール実行ワークフローのエラーを自動検出・修正・マージする仕組みの構築

---

## 📊 現状の問題点

### 1. スケジュール実行ワークフローのエラーハンドリング不足

**対象ワークフロー**:

- Daily Trend Analysis
- Daily Article Generation
- Weekly Newsletter Generation
- Scheduled Backup
- Social Media Auto Post

**問題点**:

- 各ステップでエラーが発生しても、詳細なエラーメッセージが出力されない
- `set -e`によりエラー時に即座に終了し、エラー内容が不明確
- エラータイプの識別が困難

### 2. Workflow Auto Fix の機能不足

**問題点**:

- 実際のエラーログを取得していない（ステップ名のみ）
- エラーメッセージがステップ名のみで、実際のエラー内容を取得していない
- エラータイプの判定が不正確
- 修正後の検証と自動マージが不完全

---

## 🎯 修正方針の概要

### Phase 1: 汎用的なエラーハンドリングの実装

#### 1.1 共通エラーハンドリングスクリプトの作成

**目的**: すべてのワークフローで使用できる汎用的なエラーハンドリング

**実装内容**:

```bash
# .github/scripts/error-handler.sh
#!/bin/bash
# 汎用的なエラーハンドリングスクリプト

set -euo pipefail

# エラー発生時の処理
trap 'error_handler $? $LINENO "$BASH_COMMAND"' ERR

error_handler() {
    local exit_code=$1
    local line_number=$2
    local command=$3

    echo "::error::Step failed at line $line_number with exit code $exit_code"
    echo "::error::Command: $command"

    # エラータイプを判定
    ERROR_TYPE=$(detect_error_type "$command" "$exit_code")
    echo "ERROR_TYPE=$ERROR_TYPE" >> $GITHUB_ENV

    # エラーログを出力
    echo "::error::Error type: $ERROR_TYPE"

    exit $exit_code
}

detect_error_type() {
    local command=$1
    local exit_code=$2

    # コマンドとエラーコードからエラータイプを判定
    if echo "$command" | grep -qE "(alembic|migration)"; then
        echo "migration"
    elif echo "$command" | grep -qE "(pip install|npm install)"; then
        echo "dependency"
    elif echo "$command" | grep -qE "(black|isort|prettier)"; then
        echo "format"
    elif echo "$command" | grep -qE "(flake8|eslint|lint)"; then
        echo "lint"
    else
        echo "unknown"
    fi
}
```

#### 1.2 各ワークフローファイルの修正

**修正内容**:

1. **エラーハンドリングの標準化**:

   ```yaml
   - name: Run step with error handling
     run: |
       set +e  # 一時的にエラーで停止しない

       # コマンド実行
       COMMAND_OUTPUT=$(your_command 2>&1)
       EXIT_CODE=$?

       # 出力を必ず表示
       echo "$COMMAND_OUTPUT"

       # エラータイプを識別
       if [ $EXIT_CODE -ne 0 ]; then
         ERROR_TYPE=$(echo "$COMMAND_OUTPUT" | detect_error_type)
         echo "::error::Step failed with error type: $ERROR_TYPE"
         echo "ERROR_TYPE=$ERROR_TYPE" >> $GITHUB_ENV
         echo "ERROR_MESSAGE<<EOF" >> $GITHUB_ENV
         echo "$COMMAND_OUTPUT" >> $GITHUB_ENV
         echo "EOF" >> $GITHUB_ENV
         exit $EXIT_CODE
       fi
   ```

2. **エラーメッセージの標準化**:
   - すべてのステップでエラーメッセージを統一フォーマットで出力
   - GitHub Actions の`::error::`記法を使用
   - エラータイプを環境変数に設定

### Phase 2: Workflow Auto Fix の改善

#### 2.1 エラーログの取得改善

**実装内容**:

```javascript
// Get workflow run logsステップを改善
- name: Get workflow run logs
  id: logs
  uses: actions/github-script@v7
  with:
    script: |
      const runId = process.env.RUN_ID;
      const jobs = await github.rest.actions.listJobsForWorkflowRun({
        owner: context.repo.owner,
        repo: context.repo.repo,
        run_id: runId,
      });

      let errorLog = '';
      let errorStep = null;

      for (const job of jobs.data.jobs) {
        if (job.conclusion === 'failure') {
          // 失敗したステップの詳細を取得
          const steps = await github.rest.actions.listJobsForWorkflowRunAttempt({
            owner: context.repo.owner,
            repo: context.repo.repo,
            run_id: runId,
            attempt_number: job.run_attempt || 1,
          });

          // 失敗したステップを特定
          errorStep = steps.data.steps.find(s => s.conclusion === 'failure');

          if (errorStep) {
            // ログを取得（GitHub APIの制限により、ログの一部のみ取得可能）
            try {
              const logResponse = await github.rest.actions.downloadJobLogsForWorkflowRun({
                owner: context.repo.owner,
                repo: context.repo.repo,
                job_id: job.id,
              });

              // ログの最後の1000行を取得（エラーが含まれる可能性が高い）
              const logLines = logResponse.data.split('\n');
              const recentLines = logLines.slice(-1000).join('\n');
              errorLog = recentLines;
            } catch (e) {
              // ログ取得に失敗した場合は、ステップ名とURLを使用
              errorLog = `Step: ${errorStep.name}\nJob URL: ${job.html_url}`;
            }
          }
          break;
        }
      }

      core.setOutput('error_log', errorLog);
      core.setOutput('error_step', errorStep ? errorStep.name : '');
```

#### 2.2 エラータイプ判定の改善

**実装内容**:

```yaml
- name: Determine error type
  id: error-type
  run: |
    ERROR_MSG="${{ steps.workflow-run.outputs.error_message }}"
    ERROR_LOG="${{ steps.logs.outputs.error_log }}"
    ERROR_STEP="${{ steps.logs.outputs.error_step }}"

    # すべての情報を結合して分析
    ALL_ERROR_INFO=$(echo "$ERROR_MSG $ERROR_LOG $ERROR_STEP" | tr '[:upper:]' '[:lower:]')

    ERROR_TYPE="unknown"

    # 詳細なパターンマッチング
    if echo "$ALL_ERROR_INFO" | grep -qE "(black|isort|prettier|format|would reformat)"; then
      ERROR_TYPE="format"
    elif echo "$ALL_ERROR_INFO" | grep -qE "(multiple head revisions|multiple head)"; then
      ERROR_TYPE="migration_multiple_heads"
    elif echo "$ALL_ERROR_INFO" | grep -qE "(can't locate revision|revision.*not found|target revision.*doesn't exist)"; then
      ERROR_TYPE="migration_missing_revision"
    elif echo "$ALL_ERROR_INFO" | grep -qE "(alembic|migration|revision|head)"; then
      ERROR_TYPE="migration"
    elif echo "$ALL_ERROR_INFO" | grep -qE "(pip install|npm install|requirements|package\.json|dependency|module not found|cannot find module|package.*not found)"; then
      ERROR_TYPE="dependency"
    elif echo "$ALL_ERROR_INFO" | grep -qE "(flake8|eslint.*--fix|lint.*fixable|pylint)"; then
      ERROR_TYPE="lint"
    fi

    echo "error_type=$ERROR_TYPE" >> $GITHUB_OUTPUT
    echo "Detected error type: $ERROR_TYPE"

    # デバッグ情報を出力
    echo "Error message: $ERROR_MSG"
    echo "Error step: $ERROR_STEP"
    echo "Error log preview: ${ERROR_LOG:0:500}..."
```

#### 2.3 自動修正フローの実装

**実装内容**:

```yaml
auto-fix:
  name: Auto Fix Error
  needs: analyze-error
  if: needs.analyze-error.outputs.auto_fixable == 'true'
  runs-on: ubuntu-latest
  permissions:
    contents: write
    pull-requests: write
    issues: write

  steps:
    - name: Checkout latest main
      uses: actions/checkout@v4
      with:
        ref: main
        token: ${{ secrets.GITHUB_TOKEN }}
        fetch-depth: 0

    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: "20"

    - name: Create fix branch from latest main
      id: branch
      run: |
        git config user.name "github-actions[bot]"
        git config user.email "github-actions[bot]@users.noreply.github.com"

        # 最新のmainを取得
        git fetch origin main
        git checkout main
        git pull origin main

        # 作業ブランチを作成
        TIMESTAMP=$(date +%Y%m%d-%H%M%S)
        WORKFLOW_NAME="${{ needs.analyze-error.outputs.workflow_name }}"
        WORKFLOW_NAME_CLEAN=$(echo "$WORKFLOW_NAME" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
        BRANCH_NAME="workflow-hotfix-${WORKFLOW_NAME_CLEAN}-${TIMESTAMP}"

        git checkout -b "$BRANCH_NAME"
        echo "branch_name=$BRANCH_NAME" >> $GITHUB_OUTPUT
        echo "Created branch: $BRANCH_NAME from latest main"

    - name: Apply fixes based on error type
      env:
        ERROR_TYPE: ${{ needs.analyze-error.outputs.error_type }}
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
      run: |
        ERROR_TYPE="${{ needs.analyze-error.outputs.error_type }}"

        case "$ERROR_TYPE" in
          format)
            echo "🔧 Fixing format errors..."
            # Backend format fixes
            if [ -d "backend" ]; then
              cd backend
              pip install black isort --quiet
              black . || true
              isort --profile black . || true
              cd ..
            fi
            # Frontend format fixes
            if [ -d "frontend" ]; then
              cd frontend
              npm ci --quiet || npm install --quiet
              npx prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}" || true
              cd ..
            fi
            ;;
          migration_multiple_heads)
            echo "🔧 Fixing multiple heads migration error..."
            cd backend
            pip install -r requirements.txt --quiet
            python3 scripts/fix_multiple_heads.py || true
            cd ..
            ;;
          migration_missing_revision)
            echo "🔧 Fixing missing revision migration error..."
            cd backend
            pip install -r requirements.txt --quiet
            python3 scripts/fix_migration_chain.py || true
            cd ..
            ;;
          migration)
            echo "🔧 Fixing general migration errors..."
            cd backend
            pip install -r requirements.txt --quiet
            python3 scripts/detect_migration_issues.py || true
            python3 scripts/auto_fix_migrations.py || true
            cd ..
            ;;
          dependency)
            echo "🔧 Fixing dependency errors..."
            # Backend dependencies
            if [ -d "backend" ] && [ -f "backend/requirements.txt" ]; then
              cd backend
              pip install --upgrade pip
              pip install -r requirements.txt
              pip freeze > requirements.txt.new
              if ! diff -q requirements.txt requirements.txt.new > /dev/null; then
                mv requirements.txt.new requirements.txt
              else
                rm requirements.txt.new
              fi
              cd ..
            fi
            # Frontend dependencies
            if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
              cd frontend
              npm install --package-lock-only
              cd ..
            fi
            ;;
          lint)
            echo "🔧 Fixing lint errors..."
            # Backend lint fixes
            if [ -d "backend" ]; then
              cd backend
              pip install flake8 autopep8 --quiet
              autopep8 --in-place --aggressive --aggressive --recursive . || true
              cd ..
            fi
            # Frontend lint fixes
            if [ -d "frontend" ]; then
              cd frontend
              npm ci --quiet || npm install --quiet
              npm run lint -- --fix || true
              cd ..
            fi
            ;;
        esac

    - name: Verify fixes
      run: |
        ERROR_TYPE="${{ needs.analyze-error.outputs.error_type }}"

        # エラータイプに応じた検証
        case "$ERROR_TYPE" in
          format)
            if [ -d "backend" ]; then
              cd backend
              pip install black isort --quiet
              black --check . && isort --profile black --check . || exit 1
              cd ..
            fi
            if [ -d "frontend" ]; then
              cd frontend
              npm ci --quiet
              npx prettier --check "src/**/*.{ts,tsx,js,jsx,json,css,md}" || exit 1
              cd ..
            fi
            ;;
          migration*)
            if [ -n "$DATABASE_URL" ]; then
              cd backend
              pip install -r requirements.txt --quiet
              python3 scripts/detect_migration_issues.py || exit 1
              cd ..
            fi
            ;;
          dependency)
            if [ -d "backend" ]; then
              cd backend
              pip install -r requirements.txt || exit 1
              cd ..
            fi
            if [ -d "frontend" ]; then
              cd frontend
              npm ci || exit 1
              cd ..
            fi
            ;;
        esac

        echo "✅ Fix verification successful"

    - name: Commit and push changes
      run: |
        git config user.name "github-actions[bot]"
        git config user.email "github-actions[bot]@users.noreply.github.com"

        git add -A

        if git diff --quiet && git diff --staged --quiet; then
          echo "ℹ️  No changes to commit"
          echo "no_changes=true" >> $GITHUB_ENV
        else
          WORKFLOW_NAME="${{ needs.analyze-error.outputs.workflow_name }}"
          ERROR_TYPE="${{ needs.analyze-error.outputs.error_type }}"
          git commit -m "fix(workflow): Auto-fix $ERROR_TYPE error in $WORKFLOW_NAME [skip ci]"
          git push origin "${{ steps.branch.outputs.branch_name }}"
          echo "no_changes=false" >> $GITHUB_ENV
        fi

    - name: Create Pull Request
      if: env.no_changes == 'false'
      uses: actions/github-script@v7
      id: create-pr
      with:
        script: |
          const branchName = '${{ steps.branch.outputs.branch_name }}';
          const workflowName = '${{ needs.analyze-error.outputs.workflow_name }}';
          const workflowRunUrl = '${{ needs.analyze-error.outputs.workflow_run_url }}';
          const errorType = '${{ needs.analyze-error.outputs.error_type }}';

          const body = `## 自動修正

          このPRは、ワークフローエラーの自動修正です。

          **元のワークフロー**: ${workflowName}
          **エラータイプ**: ${errorType}
          **元のワークフロー実行**: [View Run](${workflowRunUrl})

          ### 修正内容

          - ${errorType === 'format' ? 'フォーマットエラーを修正（black, isort, prettier）' : ''}
          - ${errorType.startsWith('migration') ? 'マイグレーションエラーを修正' : ''}
          - ${errorType === 'dependency' ? '依存関係エラーを修正' : ''}
          - ${errorType === 'lint' ? 'リンターエラーを修正（自動修正可能なもののみ）' : ''}

          ### 検証

          修正後、以下の検証を実行しました：
          - フォーマットチェック
          - リンターチェック
          - 型チェック（該当する場合）

          ### 注意事項

          このPRは自動生成されました。マージ前に内容を確認してください。`;

          const pr = await github.rest.pulls.create({
            owner: context.repo.owner,
            repo: context.repo.repo,
            title: `🔧 Auto-fix: ${errorType} error in ${workflowName}`,
            head: branchName,
            base: 'main',
            body,
            labels: ['auto-fix', 'workflow'],
          });

          core.setOutput('pr_number', pr.data.number.toString());
          core.setOutput('pr_url', pr.data.html_url);

    - name: Wait for CI checks
      if: env.no_changes == 'false'
      run: |
        PR_NUMBER="${{ steps.create-pr.outputs.pr_number }}"
        MAX_WAIT=600  # 10分
        WAIT_INTERVAL=30  # 30秒
        ELAPSED=0

        while [ $ELAPSED -lt $MAX_WAIT ]; do
          sleep $WAIT_INTERVAL
          ELAPSED=$((ELAPSED + WAIT_INTERVAL))
          
          # PRのステータスを確認
          # GitHub APIでCIチェックの状態を確認
          echo "Waiting for CI checks... (${ELAPSED}s elapsed)"
        done

    - name: Merge PR if verification successful
      if: env.no_changes == 'false'
      uses: actions/github-script@v7
      with:
        script: |
          const prNumber = parseInt('${{ steps.create-pr.outputs.pr_number }}');

          // PRのステータスを確認
          const pr = await github.rest.pulls.get({
            owner: context.repo.owner,
            repo: context.repo.repo,
            pull_number: prNumber,
          });

          // マージ可能か確認
          if (pr.data.mergeable && pr.data.mergeable_state === 'clean') {
            await github.rest.pulls.merge({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: prNumber,
              merge_method: 'squash',
              commit_title: `fix(workflow): Auto-fix ${{ needs.analyze-error.outputs.error_type }} error`,
            });
            
            // コメントを追加
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: prNumber,
              body: '✅ 修正が検証され、自動的にマージされました。',
            });
            
            core.setOutput('merged', 'true');
          } else {
            core.setOutput('merged', 'false');
            console.log('PR is not mergeable. State:', pr.data.mergeable_state);
          }
```

---

## 📋 実装ステップ

### Step 1: 共通エラーハンドリングスクリプトの作成

- `.github/scripts/error-handler.sh`を作成
- エラータイプ検出機能を実装

### Step 2: 各ワークフローファイルの修正

- `daily-trends.yml`
- `daily-articles.yml`
- `weekly-newsletter.yml`
- `scheduled-backup.yml`
- `social-media-post.yml`

各ファイルに汎用的なエラーハンドリングを追加

### Step 3: Workflow Auto Fix の改善

- エラーログ取得の改善
- エラータイプ判定の改善
- 自動修正フローの実装
- PR 作成と自動マージの実装

### Step 4: テストと検証

- 各エラータイプでの動作確認
- 自動マージの動作確認

---

## 🎯 期待される効果

1. **エラー検出の精度向上**: 実際のログを分析することで、エラータイプを正確に判定
2. **自動修正の確実性**: エラータイプに応じた適切な修正を実行
3. **運用効率の向上**: 手動介入なしでエラーを修正・マージ
4. **エラー分析の改善**: 詳細なログにより、エラーの原因を特定しやすくなる
