/**
 * Design System Tokens
 * 
 * Centralized design tokens for consistent theming across the application.
 * Includes colors, typography, spacing, and animation configurations.
 */

export const colors = {
    // Brand Colors - Sophisticated purple-blue gradient
    brand: {
        50: '#f0f4ff',
        100: '#e0e7ff',
        200: '#c7d2fe',
        300: '#a5b4fc',
        400: '#818cf8',
        500: '#6366f1', // Primary
        600: '#4f46e5',
        700: '#4338ca',
        800: '#3730a3',
        900: '#312e81',
    },

    // Neutral - Warm grays
    neutral: {
        50: '#fafaf9',
        100: '#f5f5f4',
        200: '#e7e5e4',
        300: '#d6d3d1',
        400: '#a8a29e',
        500: '#78716c',
        600: '#57534e',
        700: '#44403c',
        800: '#292524',
        900: '#1c1917',
    },

    // Semantic Colors
    success: {
        light: '#d1fae5',
        DEFAULT: '#10b981',
        dark: '#065f46',
    },
    warning: {
        light: '#fef3c7',
        DEFAULT: '#f59e0b',
        dark: '#92400e',
    },
    error: {
        light: '#fee2e2',
        DEFAULT: '#ef4444',
        dark: '#7f1d1d',
    },
    info: {
        light: '#dbeafe',
        DEFAULT: '#3b82f6',
        dark: '#1e3a8a',
    },

    // Confidence Indicators
    confidence: {
        high: { bg: '#d1fae5', text: '#065f46', border: '#10b981' },
        medium: { bg: '#fef3c7', text: '#92400e', border: '#f59e0b' },
        low: { bg: '#fee2e2', text: '#7f1d1d', border: '#ef4444' },
    },

    // Severity Colors
    severity: {
        critical: { bg: '#fee2e2', text: '#7f1d1d', border: '#ef4444' },
        major: { bg: '#fef3c7', text: '#92400e', border: '#f59e0b' },
        minor: { bg: '#ccfbf1', text: '#0f766e', border: '#14b8a6' },
        informational: { bg: '#dbeafe', text: '#1e3a8a', border: '#3b82f6' },
    },
} as const;

export const typography = {
    fonts: {
        sans: "'Inter Variable', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        mono: "'JetBrains Mono', 'Fira Code', 'Courier New', monospace",
        display: "'Cal Sans', 'Inter Variable', sans-serif",
    },
    sizes: {
        xs: '0.75rem',    // 12px
        sm: '0.875rem',   // 14px
        base: '1rem',     // 16px
        lg: '1.125rem',   // 18px
        xl: '1.25rem',    // 20px
        '2xl': '1.5rem',  // 24px
        '3xl': '1.875rem',// 30px
        '4xl': '2.25rem', // 36px
        '5xl': '3rem',    // 48px
        '6xl': '3.75rem', // 60px
        '7xl': '4.5rem',  // 72px
    },
    weights: {
        light: 300,
        normal: 400,
        medium: 500,
        semibold: 600,
        bold: 700,
        extrabold: 800,
    },
    lineHeights: {
        none: 1,
        tight: 1.25,
        snug: 1.375,
        normal: 1.5,
        relaxed: 1.625,
        loose: 2,
    },
} as const;

export const spacing = {
    xs: '0.25rem',   // 4px
    sm: '0.5rem',    // 8px
    md: '1rem',      // 16px
    lg: '1.5rem',    // 24px
    xl: '2rem',      // 32px
    '2xl': '3rem',   // 48px
    '3xl': '4rem',   // 64px
    '4xl': '6rem',   // 96px
    '5xl': '8rem',   // 128px
} as const;

export const borderRadius = {
    none: '0',
    sm: '0.25rem',   // 4px
    md: '0.5rem',    // 8px
    lg: '0.75rem',   // 12px
    xl: '1rem',      // 16px
    '2xl': '1.5rem', // 24px
    '3xl': '2rem',   // 32px
    full: '9999px',
} as const;

export const shadows = {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
    none: 'none',
} as const;

export const animations = {
    durations: {
        fast: '150ms',
        normal: '300ms',
        slow: '500ms',
        slower: '1000ms',
    },
    easings: {
        linear: 'linear',
        easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
        easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
        easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
        spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    },
} as const;

export const breakpoints = {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
} as const;

export const zIndex = {
    base: 0,
    dropdown: 1000,
    sticky: 1100,
    fixed: 1200,
    modalBackdrop: 1300,
    modal: 1400,
    popover: 1500,
    tooltip: 1600,
} as const;

// Helper function to get confidence variant
export function getConfidenceVariant(confidence: number): 'high' | 'medium' | 'low' {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.5) return 'medium';
    return 'low';
}

// Helper function to get severity variant
export function getSeverityVariant(severity: string): 'critical' | 'major' | 'minor' | 'informational' {
    const normalized = severity.toLowerCase();
    if (normalized === 'critical') return 'critical';
    if (normalized === 'major') return 'major';
    if (normalized === 'minor') return 'minor';
    return 'informational';
}
