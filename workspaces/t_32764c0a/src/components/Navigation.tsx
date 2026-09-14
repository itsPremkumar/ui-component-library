import React, { useState, useCallback } from 'react';
import { Theme, ThemeMode, getTheme } from '../theme';

export interface NavItem {
  /** Item label */
  label: string;
  /** Item href */
  href?: string;
  /** Item icon */
  icon?: React.ReactNode;
  /** Active state */
  active?: boolean;
  /** Disabled state */
  disabled?: boolean;
  /** Sub-items */
  children?: NavItem[];
  /** Click handler */
  onClick?: () => void;
}

export interface NavigationProps {
  /** Navigation items */
  items: NavItem[];
  /** Navigation variant */
  variant?: 'horizontal' | 'vertical' | 'sidebar';
  /** Brand/logo element */
  brand?: React.ReactNode;
  /** Theme mode */
  themeMode?: ThemeMode;
  /** Collapsible (for sidebar) */
  collapsible?: boolean;
  /** Collapsed state */
  defaultCollapsed?: boolean;
  /** Fixed position */
  fixed?: boolean;
  /** Background color override */
  backgroundColor?: string;
}

export function Navigation({
  items,
  variant = 'horizontal',
  brand,
  themeMode = 'light',
  collapsible = false,
  defaultCollapsed = false,
  fixed = false,
  backgroundColor,
}: NavigationProps) {
  const theme = getTheme(themeMode);
  const [collapsed, setCollapsed] = useState(defaultCollapsed);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

  const handleToggleCollapse = useCallback(() => {
    if (collapsible) {
      setCollapsed((prev) => !prev);
    }
  }, [collapsible]);

  const navStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: variant === 'horizontal' ? 'row' : 'column',
    alignItems: variant === 'horizontal' ? 'center' : 'stretch',
    gap: variant === 'horizontal' ? theme.spacing.lg : theme.spacing.xs,
    padding: variant === 'horizontal' ? `${theme.spacing.sm} ${theme.spacing.lg}` : theme.spacing.md,
    backgroundColor: backgroundColor || theme.colors.surface,
    borderBottom: variant === 'horizontal' ? `1px solid ${theme.colors.border}` : undefined,
    borderRight: variant === 'vertical' || variant === 'sidebar' ? `1px solid ${theme.colors.border}` : undefined,
    position: fixed ? 'sticky' : 'relative',
    top: fixed ? 0 : undefined,
    zIndex: theme.zIndex.sticky,
    width: variant === 'sidebar' ? (collapsed ? '60px' : '240px') : '100%',
    minHeight: variant !== 'horizontal' ? '100vh' : undefined,
    transition: `width ${theme.transitions.normal}`,
    fontFamily: theme.typography.fontFamily,
  };

  const brandStyles: React.CSSProperties = {
    fontSize: theme.typography.fontSize.xl,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text,
    padding: theme.spacing.sm,
    whiteSpace: 'nowrap',
    overflow: 'hidden',
  };

  const itemBaseStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.sm,
    padding: `${theme.spacing.sm} ${theme.spacing.md}`,
    borderRadius: theme.borderRadius.md,
    color: theme.colors.text,
    textDecoration: 'none',
    cursor: 'pointer',
    transition: `background-color ${theme.transitions.fast}, color ${theme.transitions.fast}`,
    whiteSpace: 'nowrap',
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.medium,
  };

  const itemActiveStyles: React.CSSProperties = {
    backgroundColor: `${theme.colors.primary}15`,
    color: theme.colors.primary,
  };

  const itemDisabledStyles: React.CSSProperties = {
    opacity: 0.5,
    cursor: 'not-allowed',
  };

  const dropdownStyles: React.CSSProperties = {
    position: 'relative',
  };

  const dropdownMenuStyles: React.CSSProperties = {
    position: 'absolute',
    top: '100%',
    left: 0,
    minWidth: '180px',
    backgroundColor: theme.colors.background,
    border: `1px solid ${theme.colors.border}`,
    borderRadius: theme.borderRadius.md,
    boxShadow: theme.shadows.lg,
    padding: theme.spacing.xs,
    zIndex: theme.zIndex.dropdown,
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing.xs,
  };

  const sidebarItemStyles: React.CSSProperties = {
    ...itemBaseStyles,
    width: '100%',
    justifyContent: collapsed ? 'center' : 'flex-start',
  };

  const toggleButtonStyles: React.CSSProperties = {
    background: 'transparent',
    border: 'none',
    cursor: 'pointer',
    padding: theme.spacing.sm,
    color: theme.colors.textSecondary,
    fontSize: '1.25rem',
    alignSelf: collapsed ? 'center' : 'flex-end',
  };

  const renderNavItem = (item: NavItem, index: number) => {
    const isActive = item.active;
    const isDisabled = item.disabled;
    const hasChildren = item.children && item.children.length > 0;

    const handleClick = () => {
      if (isDisabled) return;
      if (hasChildren) {
        setActiveDropdown(activeDropdown === item.label ? null : item.label);
      }
      item.onClick?.();
    };

    if (variant === 'sidebar') {
      return (
        <div key={index} style={dropdownStyles}>
          <div
            style={{
              ...sidebarItemStyles,
              ...(isActive ? itemActiveStyles : {}),
              ...(isDisabled ? itemDisabledStyles : {}),
            }}
            onClick={handleClick}
            role="button"
            tabIndex={isDisabled ? -1 : 0}
            aria-expanded={hasChildren ? activeDropdown === item.label : undefined}
            aria-disabled={isDisabled}
          >
            {item.icon && <span aria-hidden="true">{item.icon}</span>}
            {!collapsed && (
              <>
                <span>{item.label}</span>
                {hasChildren && (
                  <span style={{ marginLeft: 'auto', fontSize: '0.75rem' }} aria-hidden="true">
                    {activeDropdown === item.label ? '▲' : '▼'}
                  </span>
                )}
              </>
            )}
          </div>
          {hasChildren && activeDropdown === item.label && !collapsed && (
            <div style={{ paddingLeft: theme.spacing.lg, display: 'flex', flexDirection: 'column', gap: theme.spacing.xs }}>
              {item.children!.map((child, childIdx) => (
                <div
                  key={childIdx}
                  style={{
                    ...itemBaseStyles,
                    padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                    ...(child.active ? itemActiveStyles : {}),
                  }}
                  onClick={child.onClick}
                  role="button"
                  tabIndex={0}
                >
                  {child.label}
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }

    if (variant === 'horizontal') {
      return (
        <div key={index} style={dropdownStyles}>
          <div
            style={{
              ...itemBaseStyles,
              ...(isActive ? itemActiveStyles : {}),
              ...(isDisabled ? itemDisabledStyles : {}),
            }}
            onClick={handleClick}
            role="button"
            tabIndex={isDisabled ? -1 : 0}
            aria-expanded={hasChildren ? activeDropdown === item.label : undefined}
            aria-disabled={isDisabled}
          >
            {item.icon && <span aria-hidden="true">{item.icon}</span>}
            <span>{item.label}</span>
            {hasChildren && (
              <span style={{ fontSize: '0.75rem' }} aria-hidden="true">
                {activeDropdown === item.label ? '▲' : '▼'}
              </span>
            )}
          </div>
          {hasChildren && activeDropdown === item.label && (
            <div style={dropdownMenuStyles}>
              {item.children!.map((child, childIdx) => (
                <div
                  key={childIdx}
                  style={{
                    ...itemBaseStyles,
                    ...(child.active ? itemActiveStyles : {}),
                  }}
                  onClick={() => {
                    child.onClick?.();
                    setActiveDropdown(null);
                  }}
                  role="button"
                  tabIndex={0}
                >
                  {child.icon && <span aria-hidden="true">{child.icon}</span>}
                  {child.label}
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }

    // vertical
    return (
      <div key={index}>
        <div
          style={{
            ...itemBaseStyles,
            width: '100%',
            ...(isActive ? itemActiveStyles : {}),
            ...(isDisabled ? itemDisabledStyles : {}),
          }}
          onClick={handleClick}
          role="button"
          tabIndex={isDisabled ? -1 : 0}
          aria-disabled={isDisabled}
        >
          {item.icon && <span aria-hidden="true">{item.icon}</span>}
          <span>{item.label}</span>
        </div>
        {item.children && (
          <div style={{ paddingLeft: theme.spacing.lg, display: 'flex', flexDirection: 'column', gap: theme.spacing.xs }}>
            {item.children.map((child, childIdx) => (
              <div
                key={childIdx}
                style={{
                  ...itemBaseStyles,
                  padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                  ...(child.active ? itemActiveStyles : {}),
                }}
                onClick={child.onClick}
                role="button"
                tabIndex={0}
              >
                {child.label}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <nav style={navStyles} role="navigation" aria-label="Main navigation">
      {collapsible && (
        <button
          style={toggleButtonStyles}
          onClick={handleToggleCollapse}
          aria-label={collapsed ? 'Expand navigation' : 'Collapse navigation'}
        >
          {collapsed ? '☰' : '✕'}
        </button>
      )}
      {brand && <div style={brandStyles}>{brand}</div>}
      {items.map(renderNavItem)}
    </nav>
  );
}
