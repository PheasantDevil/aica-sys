import { z } from 'zod';

// 共通バリデーションルール
export const commonSchemas = {
  email: z.string().email('有効なメールアドレスを入力してください'),
  password: z
    .string()
    .min(8, 'パスワードは8文字以上で入力してください')
    .max(128, 'パスワードは128文字以下で入力してください')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
      'パスワードは大文字、小文字、数字、特殊文字を含む必要があります'
    ),
  name: z
    .string()
    .min(1, '名前は必須です')
    .max(100, '名前は100文字以下で入力してください')
    .regex(/^[a-zA-Z0-9\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\s]+$/, '名前は有効な文字のみ使用してください'),
  url: z.string().url('有効なURLを入力してください'),
  phone: z
    .string()
    .regex(/^[\d\-\+\(\)\s]+$/, '有効な電話番号を入力してください')
    .min(10, '電話番号は10文字以上で入力してください')
    .max(20, '電話番号は20文字以下で入力してください'),
  uuid: z.string().uuid('有効なUUIDを入力してください'),
  positiveInt: z.number().int().positive('正の整数を入力してください'),
  nonEmptyString: z.string().min(1, 'この項目は必須です'),
  safeHtml: z
    .string()
    .max(10000, 'コンテンツは10000文字以下で入力してください')
    .refine(
      (val) => !/<script|javascript:|on\w+\s*=/i.test(val),
      '危険なスクリプトが含まれています'
    ),
};

// ユーザー関連スキーマ
export const userSchemas = {
  signUp: z.object({
    name: commonSchemas.name,
    email: commonSchemas.email,
    password: commonSchemas.password,
    confirmPassword: z.string(),
  }).refine((data) => data.password === data.confirmPassword, {
    message: 'パスワードが一致しません',
    path: ['confirmPassword'],
  }),

  signIn: z.object({
    email: commonSchemas.email,
    password: z.string().min(1, 'パスワードは必須です'),
  }),

  profileUpdate: z.object({
    name: commonSchemas.name.optional(),
    email: commonSchemas.email.optional(),
    phone: commonSchemas.phone.optional(),
    bio: z.string().max(500, '自己紹介は500文字以下で入力してください').optional(),
  }),
};

// 記事関連スキーマ
export const articleSchemas = {
  create: z.object({
    title: z
      .string()
      .min(1, 'タイトルは必須です')
      .max(200, 'タイトルは200文字以下で入力してください'),
    content: commonSchemas.safeHtml,
    excerpt: z
      .string()
      .max(500, '要約は500文字以下で入力してください')
      .optional(),
    tags: z
      .array(z.string().max(50, 'タグは50文字以下で入力してください'))
      .max(10, 'タグは10個以下で入力してください')
      .optional(),
    isPublished: z.boolean().optional(),
  }),

  update: z.object({
    title: z
      .string()
      .min(1, 'タイトルは必須です')
      .max(200, 'タイトルは200文字以下で入力してください')
      .optional(),
    content: commonSchemas.safeHtml.optional(),
    excerpt: z
      .string()
      .max(500, '要約は500文字以下で入力してください')
      .optional(),
    tags: z
      .array(z.string().max(50, 'タグは50文字以下で入力してください'))
      .max(10, 'タグは10個以下で入力してください')
      .optional(),
    isPublished: z.boolean().optional(),
  }),
};

// ニュースレター関連スキーマ
export const newsletterSchemas = {
  create: z.object({
    title: z
      .string()
      .min(1, 'タイトルは必須です')
      .max(200, 'タイトルは200文字以下で入力してください'),
    content: commonSchemas.safeHtml,
    subject: z
      .string()
      .min(1, '件名は必須です')
      .max(100, '件名は100文字以下で入力してください'),
    scheduledAt: z.string().datetime().optional(),
  }),
};

// サブスクリプション関連スキーマ
export const subscriptionSchemas = {
  create: z.object({
    planId: z.enum(['free', 'premium', 'enterprise'], {
      message: '有効なプランを選択してください',
    }),
    paymentMethodId: z.string().min(1, '支払い方法を選択してください'),
  }),

  update: z.object({
    planId: z.enum(['free', 'premium', 'enterprise']).optional(),
    action: z.enum(['cancel', 'upgrade', 'downgrade']).optional(),
  }),
};

// API リクエスト用スキーマ
export const apiSchemas = {
  pagination: z.object({
    page: z.number().int().min(1).default(1),
    limit: z.number().int().min(1).max(100).default(20),
    sort: z.string().max(50).optional(),
    order: z.enum(['asc', 'desc']).default('desc'),
  }),

  search: z.object({
    q: z.string().max(100, '検索クエリは100文字以下で入力してください'),
    category: z.string().max(50).optional(),
    tags: z.array(z.string().max(50)).max(10).optional(),
  }),
};

// バリデーション関数
export function validateData<T>(schema: z.ZodSchema<T>, data: unknown): {
  success: boolean;
  data?: T;
  errors?: z.ZodError;
} {
  try {
    const validatedData = schema.parse(data);
    return { success: true, data: validatedData };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { success: false, errors: error };
    }
    throw error;
  }
}

// バリデーションエラーをフォーマット
export function formatValidationErrors(errors: z.ZodError): Record<string, string> {
  const formattedErrors: Record<string, string> = {};
  
  errors.issues.forEach((error) => {
    const path = error.path.join('.');
    formattedErrors[path] = error.message;
  });
  
  return formattedErrors;
}
