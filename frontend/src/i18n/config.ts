export const locales = ['en', 'ja'] as const;
export type Locale = typeof locales[number];

export const defaultLocale: Locale = 'ja';

export const localeNames: Record<Locale, string> = {
  en: 'English',
  ja: '日本語',
};

export const localeFlags: Record<Locale, string> = {
  en: '🇺🇸',
  ja: '🇯🇵',
};

export const rtlLocales: Locale[] = [];

export const isRTL = (locale: Locale): boolean => rtlLocales.includes(locale);

export const getDirection = (locale: Locale): 'ltr' | 'rtl' => 
  isRTL(locale) ? 'rtl' : 'ltr';
