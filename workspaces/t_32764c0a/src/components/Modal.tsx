import React, { useEffect, useCallback, forwardRef } from 'react';
import { Theme, ThemeMode, getTheme } from '../theme';

export interface ModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Close handler */
  onClose: () => void;
  /** Modal title */
  title?: string;
  /** Modal content */
  children?: React.ReactNode;
  /** Modal footer */
  footer?: React.ReactNode;
  /** Modal size */
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  /** Close on overlay click */
  closeOnOverlayClick?: boolean;
  /** Close on Escape key */
  closeOnEscape?: boolean;
  /** Close button visible */
  showCloseButton?: boolean;
  /** Theme mode */
  themeMode?: ThemeMode;
}

const getSizeStyles = (size: ModalProps['size']): React.CSSProperties => {
  switch (size) {
    case 'sm':
      return { maxWidth: '400px', width: '100%' };
    case 'lg':
      return { maxWidth: '800px', width: '100%' };
    case 'xl':
      return { maxWidth: '1140px', width: '100%' };
    case 'full':
      return { maxWidth: '100%', height: '100%', margin: 0, borderRadius: 0 };
    default:
      return { maxWidth: '560px', width: '100%' };
  }
};

export const Modal = forwardRef<HTMLDivElement, ModalProps>(
  (
    {
      isOpen,
      onClose,
      title,
      children,
      footer,
      size = 'md',
      closeOnOverlayClick = true,
      closeOnEscape = true,
      showCloseButton = true,
      themeMode = 'light',
    },
    ref
  ) => {
    const theme = getTheme(themeMode);

    const handleEscape = useCallback(
      (e: KeyboardEvent) => {
        if (closeOnEscape && e.key === 'Escape') {
          onClose();
        }
      },
      [closeOnEscape, onClose]
    );

    useEffect(() => {
      if (isOpen) {
        document.addEventListener('keydown', handleEscape);
        document.body.style.overflow = 'hidden';
      }
      return () => {
        document.removeEventListener('keydown', handleEscape);
        document.body.style.overflow = 'unset';
      };
    }, [isOpen, handleEscape]);

    if (!isOpen) return null;

    const overlayStyles: React.CSSProperties = {
      position: 'fixed',
      inset: 0,
      backgroundColor: theme.colors.overlay,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: theme.zIndex.modal,
      padding: theme.spacing.md,
      animation: 'fadeIn 200ms ease-in-out',
    };

    const modalStyles: React.CSSProperties = {
      ...getSizeStyles(size),
      backgroundColor: theme.colors.background,
      borderRadius: theme.borderRadius.lg,
      boxShadow: theme.shadows.xl,
      display: 'flex',
      flexDirection: 'column',
      maxHeight: '90vh',
      overflow: 'hidden',
      animation: 'slideUp 250ms ease-out',
    };

    const headerStyles: React.CSSProperties = {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: theme.spacing.lg,
      borderBottom: `1px solid ${theme.colors.border}`,
    };

    const titleStyles: React.CSSProperties = {
      margin: 0,
      fontSize: theme.typography.fontSize.xl,
      fontWeight: theme.typography.fontWeight.semibold,
      color: theme.colors.text,
    };

    const closeButtonStyles: React.CSSProperties = {
      background: 'transparent',
      border: 'none',
      fontSize: '1.5rem',
      cursor: 'pointer',
      color: theme.colors.textSecondary,
      padding: theme.spacing.xs,
      borderRadius: theme.borderRadius.sm,
      lineHeight: 1,
    };

    const bodyStyles: React.CSSProperties = {
      padding: theme.spacing.lg,
      overflow: 'auto',
      flex: 1,
      color: theme.colors.text,
    };

    const footerStyles: React.CSSProperties = {
      padding: theme.spacing.lg,
      borderTop: `1px solid ${theme.colors.border}`,
      display: 'flex',
      justifyContent: 'flex-end',
      gap: theme.spacing.sm,
    };

    return (
      <div
        style={overlayStyles}
        onClick={closeOnOverlayClick ? onClose : undefined}
        role="presentation"
      >
        <div
          ref={ref}
          style={modalStyles}
          onClick={(e) => e.stopPropagation()}
          role="dialog"
          aria-modal="true"
          aria-labelledby={title ? 'modal-title' : undefined}
        >
          {(title || showCloseButton) && (
            <div style={headerStyles}>
              {title && (
                <h2 id="modal-title" style={titleStyles}>
                  {title}
                </h2>
              )}
              {showCloseButton && (
                <button
                  style={closeButtonStyles}
                  onClick={onClose}
                  aria-label="Close modal"
                  type="button"
                >
                  &times;
                </button>
              )}
            </div>
          )}
          <div style={bodyStyles}>{children}</div>
          {footer && <div style={footerStyles}>{footer}</div>}
        </div>
      </div>
    );
  }
);

Modal.displayName = 'Modal';
