"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface ProgressRingProps {
    progress: number // 0 to 100
    size?: number
    strokeWidth?: number
    className?: string
    showPercentage?: boolean
}

export function ProgressRing({
    progress,
    size = 120,
    strokeWidth = 8,
    className,
    showPercentage = true,
}: ProgressRingProps) {
    const radius = (size - strokeWidth) / 2
    const circumference = radius * 2 * Math.PI
    const offset = circumference - (progress / 100) * circumference

    const getColor = () => {
        if (progress >= 80) return "stroke-success"
        if (progress >= 50) return "stroke-warning"
        return "stroke-error"
    }

    return (
        <div className={cn("relative inline-flex items-center justify-center", className)}>
            <svg width={size} height={size} className="transform -rotate-90">
                {/* Background circle */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    fill="none"
                    className="text-muted"
                />

                {/* Progress circle */}
                <motion.circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    fill="none"
                    strokeLinecap="round"
                    className={getColor()}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset: offset }}
                    transition={{ duration: 1, ease: "easeInOut" }}
                    style={{
                        strokeDasharray: circumference,
                    }}
                />
            </svg>

            {showPercentage && (
                <div className="absolute inset-0 flex items-center justify-center">
                    <motion.span
                        initial={{ opacity: 0, scale: 0.5 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.3 }}
                        className="text-2xl font-bold"
                    >
                        {Math.round(progress)}%
                    </motion.span>
                </div>
            )}
        </div>
    )
}
