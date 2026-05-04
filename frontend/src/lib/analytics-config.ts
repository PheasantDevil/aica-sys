const GA_ID_PATTERN = /^G-[A-Z0-9]+$/i;

export function getSanitizedGaId(rawValue?: string): string {
  const trimmed = (rawValue || "").trim();
  if (!trimmed) return "";
  if (!GA_ID_PATTERN.test(trimmed)) return "";
  return trimmed;
}
