import {
  commonSchemas,
  formatValidationErrors,
  userSchemas,
  validateData,
} from '../validation';

describe('Validation Schemas', () => {
  describe('commonSchemas', () => {
    it('validates email correctly', () => {
      const validEmails = ['test@example.com', 'user.name@domain.co.jp'];
      const invalidEmails = ['invalid-email', '@domain.com', 'user@'];

      validEmails.forEach(email => {
        const result = validateData(commonSchemas.email, email);
        expect(result.success).toBe(true);
      });

      invalidEmails.forEach(email => {
        const result = validateData(commonSchemas.email, email);
        expect(result.success).toBe(false);
      });
    });

    it('validates password correctly', () => {
      const validPassword = 'Password123!';
      const invalidPasswords = [
        'short', // 短すぎる
        'nouppercase123!', // 大文字なし
        'NOLOWERCASE123!', // 小文字なし
        'NoNumbers!', // 数字なし
        'NoSpecial123', // 特殊文字なし
      ];

      const result = validateData(commonSchemas.password, validPassword);
      expect(result.success).toBe(true);

      invalidPasswords.forEach(password => {
        const result = validateData(commonSchemas.password, password);
        expect(result.success).toBe(false);
      });
    });

    it('validates safe HTML correctly', () => {
      const safeHtml = '<p>This is safe content</p>';
      const maliciousHtml = '<script>alert("xss")</script>';
      const maliciousHtml2 = 'javascript:alert("xss")';

      const result1 = validateData(commonSchemas.safeHtml, safeHtml);
      expect(result1.success).toBe(true);

      const result2 = validateData(commonSchemas.safeHtml, maliciousHtml);
      expect(result2.success).toBe(false);

      const result3 = validateData(commonSchemas.safeHtml, maliciousHtml2);
      expect(result3.success).toBe(false);
    });
  });

  describe('userSchemas', () => {
    it('validates sign up data correctly', () => {
      const validData = {
        name: 'John Doe',
        email: 'john@example.com',
        password: 'Password123!',
        confirmPassword: 'Password123!',
      };

      const result = validateData(userSchemas.signUp, validData);
      expect(result.success).toBe(true);
    });

    it('rejects sign up data with mismatched passwords', () => {
      const invalidData = {
        name: 'John Doe',
        email: 'john@example.com',
        password: 'Password123!',
        confirmPassword: 'DifferentPassword123!',
      };

      const result = validateData(userSchemas.signUp, invalidData);
      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
    });

    it('validates sign in data correctly', () => {
      const validData = {
        email: 'john@example.com',
        password: 'Password123!',
      };

      const result = validateData(userSchemas.signIn, validData);
      expect(result.success).toBe(true);
    });
  });

  describe('formatValidationErrors', () => {
    it('formats validation errors correctly', () => {
      const mockError = {
        issues: [
          { path: ['email'], message: 'Invalid email' },
          { path: ['password'], message: 'Password too short' },
          { path: ['profile', 'name'], message: 'Name required' },
        ],
      } as any;

      const formatted = formatValidationErrors(mockError);
      expect(formatted).toEqual({
        email: 'Invalid email',
        password: 'Password too short',
        'profile.name': 'Name required',
      });
    });
  });
});
