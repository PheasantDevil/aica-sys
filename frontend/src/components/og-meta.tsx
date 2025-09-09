import Head from 'next/head';

interface OGMetaProps {
  title: string;
  description: string;
  url: string;
  image?: string;
  type?: 'website' | 'article';
  publishedTime?: string;
  modifiedTime?: string;
  author?: string;
  tags?: string[];
}

export function OGMeta({
  title,
  description,
  url,
  image = '/og-image.jpg',
  type = 'website',
  publishedTime,
  modifiedTime,
  author,
  tags = [],
}: OGMetaProps) {
  const fullImageUrl = image.startsWith('http') ? image : `${process.env.NEXT_PUBLIC_BASE_URL || 'https://aica-sys.com'}${image}`;
  const fullUrl = url.startsWith('http') ? url : `${process.env.NEXT_PUBLIC_BASE_URL || 'https://aica-sys.com'}${url}`;

  return (
    <Head>
      {/* 基本メタタグ */}
      <title>{title}</title>
      <meta name="description" content={description} />
      <link rel="canonical" href={fullUrl} />

      {/* Open Graph メタタグ */}
      <meta property="og:type" content={type} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={fullUrl} />
      <meta property="og:image" content={fullImageUrl} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:site_name" content="AICA-SyS" />
      <meta property="og:locale" content="ja_JP" />

      {/* Twitter Card メタタグ */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:site" content="@aica_sys" />
      <meta name="twitter:creator" content="@aica_sys" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={fullImageUrl} />

      {/* 記事固有のメタタグ */}
      {type === 'article' && (
        <>
          {publishedTime && <meta property="article:published_time" content={publishedTime} />}
          {modifiedTime && <meta property="article:modified_time" content={modifiedTime} />}
          {author && <meta property="article:author" content={author} />}
          {tags.map((tag, index) => (
            <meta key={index} property="article:tag" content={tag} />
          ))}
        </>
      )}

      {/* 追加のメタタグ */}
      <meta name="robots" content="index, follow" />
      <meta name="googlebot" content="index, follow" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
    </Head>
  );
}

// 記事用OGメタタグ
export function ArticleOGMeta({
  articleId,
  title,
  description,
  image,
  publishedTime,
  modifiedTime,
  author,
  tags,
}: {
  articleId: string;
  title: string;
  description: string;
  image?: string;
  publishedTime: string;
  modifiedTime?: string;
  author: string;
  tags: string[];
}) {
  return (
    <OGMeta
      title={title}
      description={description}
      url={`/articles/${articleId}`}
      image={image}
      type="article"
      publishedTime={publishedTime}
      modifiedTime={modifiedTime}
      author={author}
      tags={tags}
    />
  );
}

// ニュースレター用OGメタタグ
export function NewsletterOGMeta({
  newsletterId,
  title,
  description,
  image,
  publishedTime,
  modifiedTime,
  author,
  tags,
}: {
  newsletterId: string;
  title: string;
  description: string;
  image?: string;
  publishedTime: string;
  modifiedTime?: string;
  author: string;
  tags: string[];
}) {
  return (
    <OGMeta
      title={title}
      description={description}
      url={`/newsletters/${newsletterId}`}
      image={image}
      type="article"
      publishedTime={publishedTime}
      modifiedTime={modifiedTime}
      author={author}
      tags={tags}
    />
  );
}
