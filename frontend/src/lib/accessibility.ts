'use client';

export class AccessibilityUtils {
  // ARIA attributes helpers
  static generateId(prefix: string = 'id'): string {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  }

  static getAriaDescribedBy(...ids: (string | undefined)[]): string | undefined {
    const validIds = ids.filter(Boolean);
    return validIds.length > 0 ? validIds.join(' ') : undefined;
  }

  static getAriaLabelledBy(...ids: (string | undefined)[]): string | undefined {
    const validIds = ids.filter(Boolean);
    return validIds.length > 0 ? validIds.join(' ') : undefined;
  }

  // Focus management
  static trapFocus(element: HTMLElement): () => void {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as NodeListOf<HTMLElement>;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    };

    element.addEventListener('keydown', handleTabKey);
    firstElement?.focus();

    return () => {
      element.removeEventListener('keydown', handleTabKey);
    };
  }

  static focusFirstElement(element: HTMLElement): void {
    const focusableElement = element.querySelector(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as HTMLElement;

    focusableElement?.focus();
  }

  // Screen reader announcements
  static announceToScreenReader(message: string, priority: 'polite' | 'assertive' = 'polite'): void {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;

    document.body.appendChild(announcement);

    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }

  // Color contrast validation
  static getContrastRatio(color1: string, color2: string): number {
    const getLuminance = (color: string): number => {
      const rgb = this.hexToRgb(color);
      if (!rgb) return 0;

      const { r, g, b } = rgb;
      const [rs, gs, bs] = [r, g, b].map(c => {
        c = c / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      });

      return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
    };

    const lum1 = getLuminance(color1);
    const lum2 = getLuminance(color2);
    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);

    return (brightest + 0.05) / (darkest + 0.05);
  }

  static isAccessibleContrast(color1: string, color2: string, level: 'AA' | 'AAA' = 'AA'): boolean {
    const ratio = this.getContrastRatio(color1, color2);
    return level === 'AA' ? ratio >= 4.5 : ratio >= 7;
  }

  private static hexToRgb(hex: string): { r: number; g: number; b: number } | null {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  }

  // Keyboard navigation helpers
  static handleArrowKeys(
    event: KeyboardEvent,
    items: HTMLElement[],
    currentIndex: number,
    orientation: 'horizontal' | 'vertical' = 'vertical'
  ): number {
    const isVertical = orientation === 'vertical';
    const isHorizontal = orientation === 'horizontal';

    switch (event.key) {
      case isVertical ? 'ArrowDown' : 'ArrowRight':
        event.preventDefault();
        return (currentIndex + 1) % items.length;
      case isVertical ? 'ArrowUp' : 'ArrowLeft':
        event.preventDefault();
        return currentIndex === 0 ? items.length - 1 : currentIndex - 1;
      case 'Home':
        event.preventDefault();
        return 0;
      case 'End':
        event.preventDefault();
        return items.length - 1;
      default:
        return currentIndex;
    }
  }

  // Form validation helpers
  static validateFormAccessibility(form: HTMLFormElement): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];
    const requiredFields = form.querySelectorAll('[required]');
    const labels = form.querySelectorAll('label');

    // Check for required fields without labels
    requiredFields.forEach((field) => {
      const fieldId = field.getAttribute('id');
      const hasLabel = fieldId && form.querySelector(`label[for="${fieldId}"]`);
      const hasAriaLabel = field.getAttribute('aria-label') || field.getAttribute('aria-labelledby');

      if (!hasLabel && !hasAriaLabel) {
        errors.push(`Required field "${field.getAttribute('name') || 'unnamed'}" is missing a label`);
      }
    });

    // Check for labels without associated fields
    labels.forEach((label) => {
      const forAttr = label.getAttribute('for');
      if (forAttr && !form.querySelector(`#${forAttr}`)) {
        errors.push(`Label references non-existent field with id "${forAttr}"`);
      }
    });

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Skip links
  static createSkipLink(targetId: string, text: string = 'Skip to main content'): HTMLElement {
    const skipLink = document.createElement('a');
    skipLink.href = `#${targetId}`;
    skipLink.textContent = text;
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
      position: absolute;
      top: -40px;
      left: 6px;
      background: #000;
      color: #fff;
      padding: 8px;
      text-decoration: none;
      z-index: 1000;
      border-radius: 4px;
    `;

    skipLink.addEventListener('focus', () => {
      skipLink.style.top = '6px';
    });

    skipLink.addEventListener('blur', () => {
      skipLink.style.top = '-40px';
    });

    return skipLink;
  }

  // High contrast mode detection
  static isHighContrastMode(): boolean {
    if (typeof window === 'undefined') return false;
    
    return window.matchMedia('(prefers-contrast: high)').matches ||
           window.matchMedia('(prefers-contrast: more)').matches;
  }

  // Reduced motion detection
  static prefersReducedMotion(): boolean {
    if (typeof window === 'undefined') return false;
    
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  // Dark mode detection
  static prefersDarkMode(): boolean {
    if (typeof window === 'undefined') return false;
    
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  // Screen reader detection (basic)
  static isScreenReaderActive(): boolean {
    if (typeof window === 'undefined') return false;
    
    return !!(window.navigator.userAgent.includes('NVDA') ||
              window.navigator.userAgent.includes('JAWS') ||
              window.navigator.userAgent.includes('VoiceOver'));
  }
}

// React hooks for accessibility
export function useAccessibility() {
  const generateId = (prefix?: string) => AccessibilityUtils.generateId(prefix);
  const announceToScreenReader = (message: string, priority?: 'polite' | 'assertive') => 
    AccessibilityUtils.announceToScreenReader(message, priority);
  const trapFocus = (element: HTMLElement) => AccessibilityUtils.trapFocus(element);
  const focusFirstElement = (element: HTMLElement) => AccessibilityUtils.focusFirstElement(element);
  const isHighContrastMode = () => AccessibilityUtils.isHighContrastMode();
  const prefersReducedMotion = () => AccessibilityUtils.prefersReducedMotion();
  const prefersDarkMode = () => AccessibilityUtils.prefersDarkMode();

  return {
    generateId,
    announceToScreenReader,
    trapFocus,
    focusFirstElement,
    isHighContrastMode,
    prefersReducedMotion,
    prefersDarkMode,
  };
}
