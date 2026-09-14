import React, { useState, useCallback, FormHTMLAttributes, ReactNode } from 'react';
import { Theme, ThemeMode, getTheme } from '../theme';
import { Input, InputProps } from './Input';
import { Button, ButtonProps } from './Button';

export interface FormField {
  /** Field name */
  name: string;
  /** Field label */
  label: string;
  /** Field type */
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search' | 'textarea' | 'select' | 'checkbox' | 'radio';
  /** Placeholder */
  placeholder?: string;
  /** Required field */
  required?: boolean;
  /** Validation pattern */
  pattern?: string;
  /** Custom validation */
  validate?: (value: string | boolean) => string | undefined;
  /** Options for select/radio */
  options?: { label: string; value: string }[];
  /** Helper text */
  helperText?: string;
  /** Default value */
  defaultValue?: string | boolean;
}

export interface FormProps extends Omit<FormHTMLAttributes<HTMLFormElement>, 'onSubmit'> {
  /** Form fields */
  fields: FormField[];
  /** Submit handler */
  onSubmit: (values: Record<string, string | boolean>) => void;
  /** Submit button text */
  submitText?: string;
  /** Reset button text */
  resetText?: string;
  /** Show reset button */
  showReset?: boolean;
  /** Loading state */
  isLoading?: boolean;
  /** Theme mode */
  themeMode?: ThemeMode;
  /** Two column layout */
  twoColumns?: boolean;
}

export function Form({
  fields,
  onSubmit,
  submitText = 'Submit',
  resetText = 'Reset',
  showReset = false,
  isLoading = false,
  themeMode = 'light',
  twoColumns = false,
  style,
  ...props
}: FormProps) {
  const theme = getTheme(themeMode);
  const [values, setValues] = useState<Record<string, string | boolean>>(() => {
    const initial: Record<string, string | boolean> = {};
    fields.forEach((f) => {
      if (f.defaultValue !== undefined) {
        initial[f.name] = f.defaultValue;
      } else if (f.type === 'checkbox') {
        initial[f.name] = false;
      } else {
        initial[f.name] = '';
      }
    });
    return initial;
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const validateField = useCallback(
    (field: FormField, value: string | boolean): string | undefined => {
      if (field.required && (value === '' || value === false)) {
        return `${field.label} is required`;
      }
      if (field.type === 'email' && typeof value === 'string' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
          return 'Please enter a valid email address';
        }
      }
      if (field.pattern && typeof value === 'string' && value) {
        const patternRegex = new RegExp(field.pattern);
        if (!patternRegex.test(value)) {
          return `Invalid format for ${field.label}`;
        }
      }
      if (field.validate) {
        return field.validate(value);
      }
      return undefined;
    },
    []
  );

  const handleChange = (name: string, value: string | boolean) => {
    setValues((prev) => ({ ...prev, [name]: value }));
    if (touched[name]) {
      const field = fields.find((f) => f.name === name);
      if (field) {
        const error = validateField(field, value);
        setErrors((prev) => ({ ...prev, [name]: error || '' }));
      }
    }
  };

  const handleBlur = (name: string) => {
    setTouched((prev) => ({ ...prev, [name]: true }));
    const field = fields.find((f) => f.name === name);
    if (field) {
      const error = validateField(field, values[name]);
      setErrors((prev) => ({ ...prev, [name]: error || '' }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: Record<string, string> = {};
    let hasErrors = false;
    fields.forEach((field) => {
      const error = validateField(field, values[field.name]);
      if (error) {
        newErrors[field.name] = error;
        hasErrors = true;
      }
    });
    setErrors(newErrors);
    setTouched(Object.fromEntries(fields.map((f) => [f.name, true])));
    if (!hasErrors) {
      onSubmit(values);
    }
  };

  const handleReset = () => {
    const initial: Record<string, string | boolean> = {};
    fields.forEach((f) => {
      if (f.type === 'checkbox') initial[f.name] = false;
      else initial[f.name] = '';
    });
    setValues(initial);
    setErrors({});
    setTouched({});
  };

  const formStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing.lg,
    width: '100%',
    ...style,
  };

  const gridStyles: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: twoColumns ? '1fr 1fr' : '1fr',
    gap: theme.spacing.lg,
  };

  const fieldContainerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing.xs,
  };

  const textareaStyles = (error: boolean): React.CSSProperties => ({
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
    border: `2px solid ${error ? theme.colors.error : theme.colors.border}`,
    backgroundColor: theme.colors.background,
    color: theme.colors.text,
    fontFamily: theme.typography.fontFamily,
    fontSize: theme.typography.fontSize.base,
    minHeight: '100px',
    resize: 'vertical',
  });

  const selectStyles = (error: boolean): React.CSSProperties => ({
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
    border: `2px solid ${error ? theme.colors.error : theme.colors.border}`,
    backgroundColor: theme.colors.background,
    color: theme.colors.text,
    fontFamily: theme.typography.fontFamily,
    fontSize: theme.typography.fontSize.base,
  });

  const checkboxGroupStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.sm,
  };

  const checkboxStyles: React.CSSProperties = {
    width: '18px',
    height: '18px',
    accentColor: theme.colors.primary,
  };

  const labelStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.text,
  };

  const requiredStyles: React.CSSProperties = {
    color: theme.colors.error,
    marginLeft: '2px',
  };

  const renderField = (field: FormField) => {
    const value = values[field.name];
    const error = errors[field.name];
    const isTouched = touched[field.name];

    if (field.type === 'textarea') {
      return (
        <div key={field.name} style={fieldContainerStyles}>
          <label htmlFor={field.name} style={labelStyles}>
            {field.label}
            {field.required && <span style={requiredStyles}>*</span>}
          </label>
          <textarea
            id={field.name}
            name={field.name}
            value={String(value)}
            placeholder={field.placeholder}
            onChange={(e) => handleChange(field.name, e.target.value)}
            onBlur={() => handleBlur(field.name)}
            style={textareaStyles(!!error && isTouched)}
            aria-invalid={!!error && isTouched}
          />
          {error && isTouched && (
            <span style={{ fontSize: theme.typography.fontSize.xs, color: theme.colors.error }} role="alert">
              {error}
            </span>
          )}
        </div>
      );
    }

    if (field.type === 'select') {
      return (
        <div key={field.name} style={fieldContainerStyles}>
          <label htmlFor={field.name} style={labelStyles}>
            {field.label}
            {field.required && <span style={requiredStyles}>*</span>}
          </label>
          <select
            id={field.name}
            name={field.name}
            value={String(value)}
            onChange={(e) => handleChange(field.name, e.target.value)}
            onBlur={() => handleBlur(field.name)}
            style={selectStyles(!!error && isTouched)}
          >
            <option value="">Select {field.label}</option>
            {field.options?.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          {error && isTouched && (
            <span style={{ fontSize: theme.typography.fontSize.xs, color: theme.colors.error }} role="alert">
              {error}
            </span>
          )}
        </div>
      );
    }

    if (field.type === 'checkbox') {
      return (
        <div key={field.name} style={fieldContainerStyles}>
          <div style={checkboxGroupStyles}>
            <input
              type="checkbox"
              id={field.name}
              name={field.name}
              checked={Boolean(value)}
              onChange={(e) => handleChange(field.name, e.target.checked)}
              onBlur={() => handleBlur(field.name)}
              style={checkboxStyles}
              aria-invalid={!!error && isTouched}
            />
            <label htmlFor={field.name} style={labelStyles}>
              {field.label}
              {field.required && <span style={requiredStyles}>*</span>}
            </label>
          </div>
          {error && isTouched && (
            <span style={{ fontSize: theme.typography.fontSize.xs, color: theme.colors.error }} role="alert">
              {error}
            </span>
          )}
        </div>
      );
    }

    // Default: text input types
    return (
      <div key={field.name}>
        <Input
          id={field.name}
          name={field.name}
          type={field.type || 'text'}
          label={field.label}
          placeholder={field.placeholder}
          value={String(value)}
          onChange={(e) => handleChange(field.name, e.target.value)}
          onBlur={() => handleBlur(field.name)}
          error={error && isTouched ? error : undefined}
          required={field.required}
          themeMode={themeMode}
        />
      </div>
    );
  };

  return (
    <form onSubmit={handleSubmit} style={formStyles} noValidate {...props}>
      <div style={gridStyles}>
        {fields.map(renderField)}
      </div>
      <div style={{ display: 'flex', gap: theme.spacing.md, marginTop: theme.spacing.md }}>
        <Button type="submit" isLoading={isLoading} themeMode={themeMode}>
          {submitText}
        </Button>
        {showReset && (
          <Button type="button" variant="outline" onClick={handleReset} themeMode={themeMode}>
            {resetText}
          </Button>
        )}
      </div>
    </form>
  );
}
