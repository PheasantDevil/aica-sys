import { ImageResponse } from 'next/og';
import { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const title = searchParams.get('title') || 'AICA-SyS';
    const description = searchParams.get('description') || 'AI駆動型TypeScriptエコシステム特化型の自動コンテンツ生成・販売システム';
    const theme = searchParams.get('theme') || 'dark';

    const isDark = theme === 'dark';
    const bgColor = isDark ? '#000000' : '#ffffff';
    const textColor = isDark ? '#ffffff' : '#000000';
    const accentColor = '#3b82f6';

    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: bgColor,
            backgroundImage: 'linear-gradient(45deg, #1e293b 0%, #0f172a 100%)',
            fontFamily: 'Inter, sans-serif',
          }}
        >
          {/* Header */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '40px',
            }}
          >
            <div
              style={{
                width: '60px',
                height: '60px',
                borderRadius: '12px',
                backgroundColor: accentColor,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '20px',
              }}
            >
              <span
                style={{
                  fontSize: '24px',
                  fontWeight: 'bold',
                  color: 'white',
                }}
              >
                A
              </span>
            </div>
            <div
              style={{
                fontSize: '32px',
                fontWeight: 'bold',
                color: textColor,
              }}
            >
              AICA-SyS
            </div>
          </div>

          {/* Title */}
          <div
            style={{
              fontSize: '48px',
              fontWeight: 'bold',
              color: textColor,
              textAlign: 'center',
              maxWidth: '900px',
              lineHeight: '1.2',
              marginBottom: '20px',
            }}
          >
            {title}
          </div>

          {/* Description */}
          <div
            style={{
              fontSize: '24px',
              color: textColor,
              textAlign: 'center',
              maxWidth: '800px',
              opacity: 0.8,
              lineHeight: '1.4',
            }}
          >
            {description}
          </div>

          {/* Footer */}
          <div
            style={{
              position: 'absolute',
              bottom: '40px',
              right: '40px',
              display: 'flex',
              alignItems: 'center',
              fontSize: '18px',
              color: textColor,
              opacity: 0.6,
            }}
          >
            <span>TypeScript エコシステム特化型 AI プラットフォーム</span>
          </div>
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    );
  } catch (error) {
    console.error('OG image generation error:', error);
    
    // Fallback image
    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#000000',
            color: '#ffffff',
            fontSize: '24px',
          }}
        >
          AICA-SyS
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    );
  }
}
