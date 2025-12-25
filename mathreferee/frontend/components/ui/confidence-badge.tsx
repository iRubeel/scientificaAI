"use client"

import { motion } from "framer-motion"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"
import { cn } from "@/lib/utils"
import { getConfidenceVariant } from "@/lib/design-system/tokens"

interface ConfidenceBadgeProps {
    confidence: number // 0.0 to 1.0
    showIcon?: boolean
    showPercentage?: boolean
    size?: "sm" | "md" | "lg"
    className?: string
}

export function ConfidenceBadge({
    confidence,
    showIcon = true,
    showPercentage = true,
    size = "md",
    className,
}: ConfidenceBadgeProps) {
    const percentage = Math.round(confidence * 100)
    const variant = getConfidenceVariant(confidence)

    const variants = {
        high: {
            bg: "bg-success-light dark:bg-success-dark/20",
            text: "text-success-dark dark:text-success-light",
            border: "border-success",
            icon: TrendingUp,
        },
        medium: {
            bg: "bg-warning-light dark:bg-warning-dark/20",
            text: "text-warning-dark dark:text-warning-light",
            border: "border-warning",
            icon: Minus,
        },
        low: {
            bg: "bg-error-light dark:bg-error-dark/20",
            text: "text-error-dark dark:text-error-light",
            border: "border-error",
            icon: TrendingDown,
        },
    }

    const config = variants[variant]
    const Icon = config.icon

    const sizes = {
        sm: "text-xs px-2 py-1",
        md: "text-sm px-3 py-1.5",
        lg: "text-base px-4 py-2",
    }

    return (
        <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className={cn(
                "inline-flex items-center gap-1.5 rounded-full border-2 font-medium",
                config.bg,
                config.text,
                config.border,
                sizes[size],
                className
            )}
        >
            {showIcon && <Icon className="h-3.5 w-3.5" />}
            {showPercentage && <span>{percentage}%</span>}
            <span className="sr-only">Confidence: {percentage}%</span>
        </motion.div>
    )
}
