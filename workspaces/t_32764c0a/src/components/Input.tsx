import React, { InputHTMLAttributes, forwardRef, useId } from 'react';
import { Theme, ThemeMode, getTheme } from '../theme';

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Input size */
  size?: 'sm' | 'md' | 'lg';
  /** Label text */
  label?: string;
  /** Helper text below input */
  helperText?: string;
  /** Error message */
  error?: string;
  /** Success state */
  isSuccess?: boolean;
  /** Full width */
  fullWidth?: boolean;
  /** Left adornment */
  leftAdornment?: React.ReactNode;
  /** Right adornment */
  rightAdornment?: React.ReactNode;
  /** Theme mode */
  themeMode?: ThemeMode;
}

const getSizeStyles = (size: InputProps['size'], theme: Theme): React.CSSProperties => {
  switch (size) {
    case 'sm':
      return {
        padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
        fontSize: theme.typography.fontSize.sm,
      };
    case 'lg':
      return {
        padding: `${theme.spacing.md} ${theme.spacing.md}`,
        fontSize: theme.typography.fontSize.lg,
      };
    default:
      return {
        padding: `${theme.spacing.sm} ${theme.spacing.md}`,
        fontSize: theme.typography.fontSize.base,
      };
  }
};

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      size = 'md',
      label,
      helperText,
      error,
      isSuccess = false,
      fullWidth = false,
      leftAdornment,
      rightAdornment,
      themeMode = 'light',
      style,
      id: externalId,
      disabled,
      ...props
    },
    ref
  ) => {
    const theme = getTheme(themeMode);
    const generatedId = useId();
    const id = externalId || generatedId;
    const sizeStyles = getSizeStyles(size, theme);

    const inputStyles: React.CSSProperties = {
      ...sizeStyles,
      width: '100%',
      borderRadius: theme.borderRadius.md,
      border: `2px solid ${error ? theme.colors.error : isSuccess ? theme.colors.success : theme.colors.border}`,
      backgroundColor: disabled ? theme.colors.surface : theme.colors.background,
      color: theme.colors.text,
      fontFamily: theme.typography.fontFamily,
      transition: `border-color ${theme.transitions.fast}, box-shadow ${theme.transitions.fast}`,
      outline: 'none',
      boxSizing: 'border-box',
    };

    const containerStyles: React.CSSProperties = {
      display: 'flex',
      flexDirection: 'column',
      gap: theme.spacing.xs,
      width: fullWidth ? '100%' : 'auto',
    };

    const labelStyles: React.CSSProperties = {
      fontSize: theme.typography.fontSize.sm,
      fontWeight: theme.typography.fontWeight.medium,
      color: theme.colors.text,
    };

    const helperStyles: React.CSSProperties = {
      fontSize: theme.typography.fontSize.xs,
      color: error ? theme.colors.error : isSuccess ? theme.colors.success : theme.colors.textSecondary,
    };

    const wrapperStyles: React.CSSProperties = {
      display: 'flex',
      alignItems: 'center',
      position: 'relative',
    };

    const adornmentStyles: React.CSSProperties = {
      position: 'absolute',
      display: 'flex',
      alignItems: 'center',
      color: theme.colors.textSecondary,
    };

    return (
      <div style={containerStyles}>
        {label && (
          <label htmlFor={id} style={labelStyles}>
            {label}
          </label>
        )}
        <div style={wrapperStyles}>
          {leftAdornment && (
            <span style={{ ...adornmentStyles, left: theme.spacing.sm }} aria-hidden="true">
              {leftAdornment}
            </span>
          )}
          <input
            ref={ref}
            id={id}
            style={{
              ...inputStyles,
              paddingLeft: leftAdornment ? '2.5rem' : undefined,
              paddingRight: rightAdornment ? '2.5rem' : undefined,
              ...style,
            }}
            disabled={disabled}
            aria-invalid={!!error}
            aria-describedby={helperText || error ? `${id}-helper` : undefined}
            {...props}
          />
          {rightAdornment && (
            <span style={{ ...adornmentStyles, right: theme.spacing.sm }} aria-hidden="true">
              {rightAdornment}
            </span>
          )}
        </div>
        {(helperText || error) && (
          <span id={`${id}-helper`} style={helperStyles} role={error ? 'alert' : undefined}>
            {error || helperText}
          </span>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
