import { useState, useCallback } from 'react';
import { ValidationError } from '@/types/api';

interface FormValidationState {
  errors: Record<string, string>;
  isValid: boolean;
  touched: Record<string, boolean>;
}

interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => string | null;
  message?: string;
}

interface ValidationRules {
  [key: string]: ValidationRule;
}

export function useFormValidation(rules: ValidationRules) {
  const [state, setState] = useState<FormValidationState>({
    errors: {},
    isValid: true,
    touched: {},
  });

  const validateField = useCallback((name: string, value: any): string | null => {
    const rule = rules[name];
    if (!rule) return null;

    // 必須チェック
    if (rule.required && (!value || value.toString().trim() === '')) {
      return rule.message || `${name}は必須です`;
    }

    // 値が空の場合は他のバリデーションをスキップ
    if (!value || value.toString().trim() === '') {
      return null;
    }

    // 最小長チェック
    if (rule.minLength && value.toString().length < rule.minLength) {
      return rule.message || `${name}は${rule.minLength}文字以上で入力してください`;
    }

    // 最大長チェック
    if (rule.maxLength && value.toString().length > rule.maxLength) {
      return rule.message || `${name}は${rule.maxLength}文字以下で入力してください`;
    }

    // パターンチェック
    if (rule.pattern && !rule.pattern.test(value.toString())) {
      return rule.message || `${name}の形式が正しくありません`;
    }

    // カスタムバリデーション
    if (rule.custom) {
      return rule.custom(value);
    }

    return null;
  }, [rules]);

  const validateForm = useCallback((values: Record<string, any>): boolean => {
    const errors: Record<string, string> = {};
    let isValid = true;

    Object.keys(rules).forEach(fieldName => {
      const error = validateField(fieldName, values[fieldName]);
      if (error) {
        errors[fieldName] = error;
        isValid = false;
      }
    });

    setState(prev => ({
      ...prev,
      errors,
      isValid,
    }));

    return isValid;
  }, [rules, validateField]);

  const setFieldError = useCallback((name: string, error: string | null) => {
    setState(prev => {
      const newErrors = { ...prev.errors };
      if (error) {
        newErrors[name] = error;
      } else {
        delete newErrors[name];
      }

      return {
        ...prev,
        errors: newErrors,
        isValid: Object.keys(newErrors).length === 0,
      };
    });
  }, []);

  const setFieldTouched = useCallback((name: string, touched: boolean = true) => {
    setState(prev => ({
      ...prev,
      touched: {
        ...prev.touched,
        [name]: touched,
      },
    }));
  }, []);

  const setServerErrors = useCallback((serverErrors: ValidationError[]) => {
    const errors: Record<string, string> = {};
    
    serverErrors.forEach(error => {
      errors[error.field] = error.message;
    });

    setState(prev => ({
      ...prev,
      errors,
      isValid: serverErrors.length === 0,
    }));
  }, []);

  const clearErrors = useCallback(() => {
    setState(prev => ({
      ...prev,
      errors: {},
      isValid: true,
    }));
  }, []);

  const getFieldError = useCallback((name: string): string | undefined => {
    return state.errors[name];
  }, [state.errors]);

  const isFieldTouched = useCallback((name: string): boolean => {
    return state.touched[name] || false;
  }, [state.touched]);

  const hasFieldError = useCallback((name: string): boolean => {
    return !!state.errors[name];
  }, [state.errors]);

  return {
    ...state,
    validateField,
    validateForm,
    setFieldError,
    setFieldTouched,
    setServerErrors,
    clearErrors,
    getFieldError,
    isFieldTouched,
    hasFieldError,
  };
}
