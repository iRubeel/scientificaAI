'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2, AlertTriangle } from 'lucide-react';
import { LinearProgress, Box, Typography } from '@mui/material';

interface AnalysisStep {
    id: string;
    label: string;
    status: 'pending' | 'running' | 'complete' | 'error';
    detail?: string;
    progress?: number;
}

interface Props {
    steps: AnalysisStep[];
    overallProgress: number;
    currentStep?: string;
}

export default function LiveAnalysis({ steps, overallProgress, currentStep }: Props) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-br from-slate-900 to-blue-900 rounded-2xl p-8 border border-blue-500/30 shadow-2xl"
        >
            {/* Header */}
            <div className="flex items-center gap-3 mb-6">
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                >
                    <Loader2 className="w-6 h-6 text-purple-400" />
                </motion.div>
                <div>
                    <h3 className="text-2xl font-bold text-white">Analyzing with Gemini Pro 3...</h3>
                    <p className="text-blue-200 text-sm">Multi-level self-critique in progress</p>
                </div>
            </div>

            {/* Steps */}
            <div className="space-y-4 mb-6">
                <AnimatePresence mode="popLayout">
                    {steps.map((step, index) => (
                        <motion.div
                            key={step.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                            transition={{ delay: index * 0.1 }}
                            className="flex items-start gap-3"
                        >
                            {/* Status Icon */}
                            <div className="flex-shrink-0 mt-1">
                                {step.status === 'complete' && (
                                    <CheckCircle2 className="w-5 h-5 text-green-400" />
                                )}
                                {step.status === 'running' && (
                                    <motion.div
                                        animate={{ rotate: 360 }}
                                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                                    >
                                        <Loader2 className="w-5 h-5 text-blue-400" />
                                    </motion.div>
                                )}
                                {step.status === 'pending' && (
                                    <div className="w-5 h-5 rounded-full border-2 border-slate-600" />
                                )}
                                {step.status === 'error' && (
                                    <AlertTriangle className="w-5 h-5 text-red-400" />
                                )}
                            </div>

                            {/* Step Content */}
                            <div className="flex-1">
                                <div className="flex items-center justify-between">
                                    <span className={`font-medium ${step.status === 'complete' ? 'text-green-300' :
                                            step.status === 'running' ? 'text-blue-300' :
                                                step.status === 'error' ? 'text-red-300' :
                                                    'text-slate-400'
                                        }`}>
                                        {step.label}
                                    </span>
                                    {step.progress !== undefined && step.status === 'running' && (
                                        <span className="text-sm text-blue-300">
                                            {Math.round(step.progress)}%
                                        </span>
                                    )}
                                </div>

                                {/* Detail */}
                                {step.detail && (
                                    <motion.p
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: 'auto' }}
                                        className="text-sm text-slate-300 mt-1 font-mono bg-slate-800/50 px-3 py-2 rounded-lg"
                                    >
                                        {step.detail}
                                    </motion.p>
                                )}

                                {/* Progress Bar */}
                                {step.progress !== undefined && step.status === 'running' && (
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className="mt-2"
                                    >
                                        <LinearProgress
                                            variant="determinate"
                                            value={step.progress}
                                            sx={{
                                                height: 4,
                                                borderRadius: 2,
                                                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                                                '& .MuiLinearProgress-bar': {
                                                    backgroundColor: '#3b82f6',
                                                },
                                            }}
                                        />
                                    </motion.div>
                                )}
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            {/* Overall Progress */}
            <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                    <span className="text-blue-200">Overall Progress</span>
                    <span className="text-white font-semibold">{Math.round(overallProgress)}%</span>
                </div>
                <LinearProgress
                    variant="determinate"
                    value={overallProgress}
                    sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                        '& .MuiLinearProgress-bar': {
                            background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                            borderRadius: 4,
                        },
                    }}
                />
            </div>

            {/* Gemini Pro 3 Info */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="mt-6 p-4 bg-purple-500/10 border border-purple-400/30 rounded-lg"
            >
                <p className="text-sm text-purple-200">
                    💡 <strong>Gemini Pro 3</strong> is analyzing {steps.filter(s => s.status === 'complete').length} of {steps.length} steps across 8 critique categories with multi-step reasoning
                </p>
            </motion.div>
        </motion.div>
    );
}
