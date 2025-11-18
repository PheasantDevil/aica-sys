// メールテンプレートの型定義
export interface EmailTemplate {
  subject: string;
  html: string;
  text: string;
}

// ウェルカムメール
export function getWelcomeEmailTemplate(userName: string): EmailTemplate {
  return {
    subject: "AICA-SySへようこそ！",
    html: `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>ようこそ AICA-SyS</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
          <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0; font-size: 28px;">AICA-SyS</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">AI-driven Content Curation & Automated Sales System</p>
          </div>
          
          <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333; margin-top: 0;">${userName}さん、ようこそ！</h2>
            
            <p>AICA-SySにご登録いただき、ありがとうございます。TypeScriptエコシステムに特化したAI自動コンテンツ生成・販売システムで、新しい収益の機会を発見してください。</p>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
              <h3 style="color: #667eea; margin-top: 0;">次のステップ</h3>
              <ul style="margin: 0; padding-left: 20px;">
                <li>プロフィールを完成させる</li>
                <li>興味のある技術分野を選択する</li>
                <li>最初の記事を生成する</li>
                <li>収益化設定を行う</li>
              </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
              <a href="https://aica-sys.com/dashboard" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">ダッシュボードにアクセス</a>
            </div>
            
            <p style="font-size: 14px; color: #666; margin-top: 30px;">
              ご質問がございましたら、お気軽にお問い合わせください。<br>
              <a href="mailto:support@aica-sys.com" style="color: #667eea;">support@aica-sys.com</a>
            </p>
          </div>
        </body>
      </html>
    `,
    text: `
      AICA-SySへようこそ！
      
      ${userName}さん、AICA-SySにご登録いただき、ありがとうございます。
      
      TypeScriptエコシステムに特化したAI自動コンテンツ生成・販売システムで、新しい収益の機会を発見してください。
      
      次のステップ：
      - プロフィールを完成させる
      - 興味のある技術分野を選択する
      - 最初の記事を生成する
      - 収益化設定を行う
      
      ダッシュボード: https://aica-sys.com/dashboard
      
      ご質問: support@aica-sys.com
    `,
  };
}

// ニュースレター配信メール
export function getNewsletterEmailTemplate(newsletter: {
  title: string;
  content: string;
  author: string;
  publishedAt: string;
  tags: string[];
}): EmailTemplate {
  return {
    subject: `【AICA-SyS】${newsletter.title}`,
    html: `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>${newsletter.title}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
          <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">AICA-SyS Newsletter</h1>
          </div>
          
          <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333; margin-top: 0;">${newsletter.title}</h2>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
              <div style="border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 20px;">
                <p style="margin: 0; color: #666; font-size: 14px;">
                  著者: ${newsletter.author} | 公開日: ${new Date(
                    newsletter.publishedAt,
                  ).toLocaleDateString("ja-JP")}
                </p>
                <div style="margin-top: 10px;">
                  ${newsletter.tags
                    .map(
                      (tag) =>
                        `<span style="background: #e3f2fd; color: #1976d2; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px;">${tag}</span>`,
                    )
                    .join("")}
                </div>
              </div>
              
              <div style="line-height: 1.8;">
                ${newsletter.content}
              </div>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
              <a href="https://aica-sys.com/newsletters" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">すべてのニュースレターを見る</a>
            </div>
            
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
              <p style="margin: 0; font-size: 14px; color: #856404;">
                <strong>配信停止:</strong> このメールの配信を停止したい場合は、
                <a href="https://aica-sys.com/unsubscribe" style="color: #667eea;">こちら</a> から設定できます。
              </p>
            </div>
          </div>
        </body>
      </html>
    `,
    text: `
      AICA-SyS Newsletter
      
      ${newsletter.title}
      
      著者: ${newsletter.author}
      公開日: ${new Date(newsletter.publishedAt).toLocaleDateString("ja-JP")}
      タグ: ${newsletter.tags.join(", ")}
      
      ${newsletter.content}
      
      すべてのニュースレター: https://aica-sys.com/newsletters
      
      配信停止: https://aica-sys.com/unsubscribe
    `,
  };
}

// サブスクリプション確認メール
export function getSubscriptionConfirmationEmailTemplate(
  plan: string,
  amount: number,
): EmailTemplate {
  return {
    subject: "サブスクリプション開始のご確認",
    html: `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>サブスクリプション開始のご確認</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
          <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0; font-size: 28px;">✓ サブスクリプション開始</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">ご登録ありがとうございます</p>
          </div>
          
          <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333; margin-top: 0;">サブスクリプション詳細</h2>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #dee2e6;">
              <table style="width: 100%; border-collapse: collapse;">
                <tr>
                  <td style="padding: 10px 0; border-bottom: 1px solid #eee; font-weight: bold;">プラン</td>
                  <td style="padding: 10px 0; border-bottom: 1px solid #eee;">${plan}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 0; border-bottom: 1px solid #eee; font-weight: bold;">月額料金</td>
                  <td style="padding: 10px 0; border-bottom: 1px solid #eee;">¥${amount.toLocaleString()}</td>
                </tr>
                <tr>
                  <td style="padding: 10px 0; font-weight: bold;">次回請求日</td>
                  <td style="padding: 10px 0;">${new Date(
                    Date.now() + 30 * 24 * 60 * 60 * 1000,
                  ).toLocaleDateString("ja-JP")}</td>
                </tr>
              </table>
            </div>
            
            <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0;">
              <p style="margin: 0; color: #155724; font-weight: bold;">
                🎉 プレミアム機能が利用可能になりました！
              </p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
              <a href="https://aica-sys.com/dashboard" style="background: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">ダッシュボードにアクセス</a>
            </div>
            
            <p style="font-size: 14px; color: #666; margin-top: 30px;">
              サブスクリプションの管理やキャンセルは、
              <a href="https://aica-sys.com/dashboard/subscription" style="color: #667eea;">こちら</a> から行えます。
            </p>
          </div>
        </body>
      </html>
    `,
    text: `
      サブスクリプション開始のご確認
      
      サブスクリプション詳細:
      - プラン: ${plan}
      - 月額料金: ¥${amount.toLocaleString()}
      - 次回請求日: ${new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString("ja-JP")}
      
      🎉 プレミアム機能が利用可能になりました！
      
      ダッシュボード: https://aica-sys.com/dashboard
      サブスクリプション管理: https://aica-sys.com/dashboard/subscription
    `,
  };
}

// パスワードリセットメール
export function getPasswordResetEmailTemplate(resetLink: string): EmailTemplate {
  return {
    subject: "パスワードリセットのご案内",
    html: `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>パスワードリセット</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
          <div style="background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0; font-size: 28px;">パスワードリセット</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">AICA-SyS</p>
          </div>
          
          <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333; margin-top: 0;">パスワードリセットのご依頼</h2>
            
            <p>パスワードリセットのご依頼を承りました。以下のボタンをクリックして、新しいパスワードを設定してください。</p>
            
            <div style="text-align: center; margin: 30px 0;">
              <a href="${resetLink}" style="background: #dc3545; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 16px;">パスワードをリセット</a>
            </div>
            
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
              <p style="margin: 0; font-size: 14px; color: #856404;">
                <strong>注意:</strong> このリンクは24時間後に無効になります。心当たりのない場合は、このメールを無視してください。
              </p>
            </div>
            
            <p style="font-size: 14px; color: #666; margin-top: 30px;">
              ボタンがクリックできない場合は、以下のリンクをコピーしてブラウザに貼り付けてください：<br>
              <a href="${resetLink}" style="color: #667eea; word-break: break-all;">${resetLink}</a>
            </p>
          </div>
        </body>
      </html>
    `,
    text: `
      パスワードリセットのご案内
      
      パスワードリセットのご依頼を承りました。
      
      以下のリンクをクリックして、新しいパスワードを設定してください：
      ${resetLink}
      
      注意: このリンクは24時間後に無効になります。
      心当たりのない場合は、このメールを無視してください。
    `,
  };
}
