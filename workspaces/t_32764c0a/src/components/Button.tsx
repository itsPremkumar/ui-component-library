import React, { ButtonHTMLAttributes, forwardRef } from 'react';
import { Theme, ThemeMode, getTheme } from '../theme';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button variant */
  variant?: 'solid' | 'outline' | 'ghost' | 'link';
  /** Button size */
  size?: 'sm' | 'md' | 'lg';
  /** Button color scheme */
  colorScheme?: 'primary' | 'secondary' | 'danger' | 'success';
  /** Full width button */
  fullWidth?: boolean;
  /** Loading state */
  isLoading?: boolean;
  /** Left icon */
  leftIcon?: React.ReactNode;
  /** Right icon */
  rightIcon?: React.ReactNode;
  /** Theme mode */
  themeMode?: ThemeMode;
}

const getVariantStyles = (
  variant: ButtonProps['variant'],
  colorScheme: ButtonProps['colorScheme'],
  theme: Theme
): React.CSSProperties => {
  const colorMap = {
    primary: {
      bg: theme.colors.primary,
      border: theme.colors.primary,
      text: '#ffffff',
      hoverBg: theme.colors.primaryHover,
      activeBg: theme.colors.primaryActive,
    },
    secondary: {
      bg: theme.colors.secondary,
      border: theme.colors.secondary,
      text: '#ffffff',
      hoverBg: theme.colors.secondaryHover,
      activeBg: theme.colors.secondaryActive,
    },
    danger: {
      bg: theme.colors.error,
      border: theme.colors.error,
      text: '#ffffff',
      hoverBg: '#dc2626',
      activeBg: '#b91c1c',
    },
    success: {
      bg: theme.colors.success,
      border: theme.colors.success,
      text: '#ffffff',
      hoverBg: '#16a34a',
      activeBg: '#15803d',
    },
  };

  const colors = colorMap[colorScheme || 'primary'];

  const base: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: theme.spacing.sm,
    fontWeight: theme.typography.fontWeight.medium,
    borderRadius: theme.borderRadius.md,
    cursor: 'pointer',
    transition: `all ${theme.transitions.fast}`,
    border: '2px solid transparent',
    outline: 'none',
    fontFamily: theme.typography.fontFamily,
  };

  switch (variant) {
    case 'outline':
      return {
        ...base,
        backgroundColor: 'transparent',
        borderColor: colors.border,
        color: colors.text === '#ffffff' ? colors.bg : colors.text,
      };
    case 'ghost':
      return {
        ...base,
        backgroundColor: 'transparent',
        borderColor: 'transparent',
        color: colors.text === '#ffffff' ? colors.bg : colors.text,
      };
    case 'link':
      return {
        ...base,
        backgroundColor: 'transparent',
        borderColor: 'transparent',
        color: colors.bg,
        textDecoration: 'underline',
        padding: '0',
      };
    default: // solid
      return {
        ...base,
        backgroundColor: colors.bg,
        borderColor: colors.border,
        color: colors.text,
      };
  }
};

const getSizeStyles = (size: ButtonProps['size'], theme: Theme): React.CSSProperties => {
  switch (size) {
    case 'sm':
      return {
        padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
        fontSize: theme.typography.fontSize.sm,
      };
    case 'lg':
      return {
        padding: `${theme.spacing.md} ${theme.spacing.lg}`,
        fontSize: theme.typography.fontSize.lg,
      };
    default: // md
      return {
        padding: `${theme.spacing.sm} ${theme.spacing.md}`,
        fontSize: theme.typography.fontSize.base,
      };
  }
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'solid',
      size = 'md',
      colorScheme = 'primary',
      fullWidth = false,
      isLoading = false,
      leftIcon,
      rightIcon,
      themeMode = 'light',
      disabled,
      children,
      style,
      ...props
    },
    ref
  ) => {
    const theme = getTheme(themeMode);
    const variantStyles = getVariantStyles(variant, colorScheme, theme);
    const sizeStyles = getSizeStyles(size, theme);

    const combinedStyles: React.CSSProperties = {
      ...variantStyles,
      ...sizeStyles,
      ...(fullWidth ? { width: '100%' } : {}),
      ...(disabled || isLoading ? { opacity: 0.6, cursor: 'not-allowed' } : {}),
      ...style,
    };

    return (
      <button
        ref={ref}
        style={combinedStyles}
        disabled={disabled || isLoading}
        aria-busy={isLoading}
        aria-disabled={disabled}
        role="button"
        {...props}
      >
        {isLoading && (
          <span
            style={{
              width: '1em',
              height: '1em',
              border: '2px solid currentColor',
              borderTopColor: 'transparent',
              borderRadius: '50%',
              animation: 'spin 0.6s linear infinite',
            }}
            aria-hidden="true"
          />
        )}
        {leftIcon && !isLoading && <span aria-hidden="true">{leftIcon}</span>}
        {children}
        {rightIcon && <span aria-hidden="true">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';
