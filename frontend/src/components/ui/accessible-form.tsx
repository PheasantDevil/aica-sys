"use client";

import React, { forwardRef, useRef, useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { AccessibilityUtils } from "@/lib/accessibility";

interface AccessibleFormProps extends React.FormHTMLAttributes<HTMLFormElement> {
  children: React.ReactNode;
  className?: string;
  onSubmit?: (event: React.FormEvent<HTMLFormElement>) => void;
  validateOnSubmit?: boolean;
  showValidationSummary?: boolean;
}

interface FormFieldProps {
  label: string;
  error?: string;
  required?: boolean;
  children: React.ReactNode;
  className?: string;
  description?: string;
  hint?: string;
}

export const AccessibleForm = forwardRef<HTMLFormElement, AccessibleFormProps>(
  (
    {
      children,
      className,
      onSubmit,
      validateOnSubmit = true,
      showValidationSummary = true,
      ...props
    },
    ref,
  ) => {
    const formRef = useRef<HTMLFormElement>(null);
    const [errors, setErrors] = useState<string[]>([]);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Combine refs
    React.useImperativeHandle(ref, () => formRef.current!);

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      setIsSubmitting(true);

      try {
        if (validateOnSubmit && formRef.current) {
          const validation = AccessibilityUtils.validateFormAccessibility(formRef.current);
          if (!validation.isValid) {
            setErrors(validation.errors);
            AccessibilityUtils.announceToScreenReader(
              `Form validation failed. ${validation.errors.length} error${
                validation.errors.length > 1 ? "s" : ""
              } found.`,
              "assertive",
            );
            return;
          }
        }

        if (onSubmit) {
          await onSubmit(event);
        }
      } finally {
        setIsSubmitting(false);
      }
    };

    return (
      <form
        ref={formRef}
        className={cn("space-y-6", className)}
        onSubmit={handleSubmit}
        noValidate
        {...props}
      >
        {showValidationSummary && errors.length > 0 && (
          <div
            role="alert"
            aria-live="polite"
            className="rounded-md bg-red-50 p-4 border border-red-200"
          >
            <h3 className="text-sm font-medium text-red-800 mb-2">
              Please correct the following errors:
            </h3>
            <ul className="list-disc list-inside text-sm text-red-700 space-y-1">
              {errors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </div>
        )}
        {children}
      </form>
    );
  },
);

AccessibleForm.displayName = "AccessibleForm";

export const FormField = forwardRef<HTMLDivElement, FormFieldProps>(
  ({ label, error, required = false, children, className, description, hint }, ref) => {
    const fieldId = AccessibilityUtils.generateId("field");
    const errorId = AccessibilityUtils.generateId("error");
    const descriptionId = AccessibilityUtils.generateId("description");
    const hintId = AccessibilityUtils.generateId("hint");

    const describedBy = AccessibilityUtils.getAriaDescribedBy(
      error ? errorId : undefined,
      description ? descriptionId : undefined,
      hint ? hintId : undefined,
    );

    return (
      <div ref={ref} className={cn("space-y-2", className)}>
        <label htmlFor={fieldId} className="block text-sm font-medium text-gray-700">
          {label}
          {required && (
            <span className="text-red-500 ml-1" aria-label="required">
              *
            </span>
          )}
        </label>

        {description && (
          <p id={descriptionId} className="text-sm text-gray-600">
            {description}
          </p>
        )}

        {hint && (
          <p id={hintId} className="text-sm text-gray-500">
            {hint}
          </p>
        )}

        <div className="relative">
          {React.cloneElement(children as React.ReactElement, {
            id: fieldId,
            "aria-invalid": error ? "true" : "false",
            "aria-describedby": describedBy,
            "aria-required": required,
          })}
        </div>

        {error && (
          <p id={errorId} role="alert" aria-live="polite" className="text-sm text-red-600">
            {error}
          </p>
        )}
      </div>
    );
  },
);

FormField.displayName = "FormField";

interface AccessibleInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  required?: boolean;
  description?: string;
  hint?: string;
  className?: string;
}

export const AccessibleInput = forwardRef<HTMLInputElement, AccessibleInputProps>(
  ({ label, error, required = false, description, hint, className, ...props }, ref) => {
    const fieldId = AccessibilityUtils.generateId("input");
    const errorId = AccessibilityUtils.generateId("error");
    const descriptionId = AccessibilityUtils.generateId("description");
    const hintId = AccessibilityUtils.generateId("hint");

    const describedBy = AccessibilityUtils.getAriaDescribedBy(
      error ? errorId : undefined,
      description ? descriptionId : undefined,
      hint ? hintId : undefined,
    );

    return (
      <FormField
        label={label}
        error={error}
        required={required}
        description={description}
        hint={hint}
      >
        <input
          ref={ref}
          id={fieldId}
          className={cn(
            "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-red-500 focus-visible:ring-red-500",
            className,
          )}
          aria-invalid={error ? "true" : "false"}
          aria-describedby={describedBy}
          aria-required={required}
          {...props}
        />
      </FormField>
    );
  },
);

AccessibleInput.displayName = "AccessibleInput";

interface AccessibleTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  error?: string;
  required?: boolean;
  description?: string;
  hint?: string;
  className?: string;
}

export const AccessibleTextarea = forwardRef<HTMLTextAreaElement, AccessibleTextareaProps>(
  ({ label, error, required = false, description, hint, className, ...props }, ref) => {
    const fieldId = AccessibilityUtils.generateId("textarea");
    const errorId = AccessibilityUtils.generateId("error");
    const descriptionId = AccessibilityUtils.generateId("description");
    const hintId = AccessibilityUtils.generateId("hint");

    const describedBy = AccessibilityUtils.getAriaDescribedBy(
      error ? errorId : undefined,
      description ? descriptionId : undefined,
      hint ? hintId : undefined,
    );

    return (
      <FormField
        label={label}
        error={error}
        required={required}
        description={description}
        hint={hint}
      >
        <textarea
          ref={ref}
          id={fieldId}
          className={cn(
            "flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-red-500 focus-visible:ring-red-500",
            className,
          )}
          aria-invalid={error ? "true" : "false"}
          aria-describedby={describedBy}
          aria-required={required}
          {...props}
        />
      </FormField>
    );
  },
);

AccessibleTextarea.displayName = "AccessibleTextarea";
