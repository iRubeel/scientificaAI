'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, AlertTriangle, AlertCircle, Info, TrendingUp, Download, Share2 } from 'lucide-react';
import { Button, Chip, LinearProgress } from '@mui/material';

interface Critique {
    type: string;
    count: number;
    severity: 'critical' | 'major' | 'minor' | 'informational';
}

interface Props {
    recommendation: string;
    confidence: number;
    summary: string;
    strengths: string[];
    weaknesses: string[];
    critiques: Critique[];
    paperTitle: string;
}

export default function ResultsDashboard({
    recommendation,
    confidence,
    summary,
    strengths,
    weaknesses,
    critiques,
    paperTitle
}: Props) {
    const getRecommendationColor = (rec: string) => {
        if (rec.toLowerCase().includes('accept')) return 'success';
        if (rec.toLowerCase().includes('reject')) return 'error';
        return 'warning';
    };

    const getSeverityIcon = (severity: string) => {
        switch (severity) {
            case 'critical': return <AlertCircle className="w-4 h-4" />;
            case 'major': return <AlertTriangle className="w-4 h-4" />;
            case 'minor': return <Info className="w-4 h-4" />;
            default: return <Info className="w-4 h-4" />;
        }
    };

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'critical': return 'error';
            case 'major': return 'warning';
            case 'minor': return 'info';
            default: return 'default';
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
        >
            {/* Success Header */}
            <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200 }}
                className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-8 text-white shadow-2xl"
            >
                <div className="flex items-center gap-3 mb-4">
                    <CheckCircle2 className="w-8 h-8" />
                    <h2 className="text-3xl font-bold">Review Complete!</h2>
                </div>
                <p className="text-green-50 text-lg">{paperTitle}</p>
            </motion.div>

            {/* Main Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Recommendation */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white rounded-2xl p-6 shadow-lg border border-slate-200"
                >
                    <h3 className="text-sm font-medium text-slate-600 mb-2">Recommendation</h3>
                    <Chip
                        label={recommendation}
                        color={getRecommendationColor(recommendation) as any}
                        size="large"
                        sx={{ fontSize: '1.125rem', fontWeight: 600, px: 2, py: 3 }}
                    />
                </motion.div>

                {/* Confidence */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-white rounded-2xl p-6 shadow-lg border border-slate-200"
                >
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium text-slate-600">Confidence Score</h3>
                        <TrendingUp className="w-5 h-5 text-blue-500" />
                    </div>
                    <div className="flex items-end gap-2 mb-3">
                        <motion.span
                            initial={{ opacity: 0, scale: 0.5 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.3, type: 'spring' }}
                            className="text-4xl font-bold text-blue-600"
                        >
                            {Math.round(confidence * 100)}%
                        </motion.span>
                    </div>
                    <LinearProgress
                        variant="determinate"
                        value={confidence * 100}
                        sx={{
                            height: 8,
                            borderRadius: 4,
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            '& .MuiLinearProgress-bar': {
                                background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                                borderRadius: 4,
                            },
                        }}
                    />
                </motion.div>
            </div>

            {/* Critique Breakdown */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-white rounded-2xl p-6 shadow-lg border border-slate-200"
            >
                <h3 className="text-xl font-bold text-slate-900 mb-4">Critique Breakdown</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {critiques.map((critique, index) => (
                        <motion.div
                            key={critique.type}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.4 + index * 0.05 }}
                            className="flex items-center justify-between p-4 bg-slate-50 rounded-xl hover:bg-slate-100 transition-colors cursor-pointer"
                        >
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg ${critique.severity === 'critical' ? 'bg-red-100 text-red-600' :
                                        critique.severity === 'major' ? 'bg-orange-100 text-orange-600' :
                                            critique.severity === 'minor' ? 'bg-blue-100 text-blue-600' :
                                                'bg-slate-100 text-slate-600'
                                    }`}>
                                    {getSeverityIcon(critique.severity)}
                                </div>
                                <div>
                                    <p className="font-medium text-slate-900 capitalize">
                                        {critique.type.replace(/_/g, ' ')}
                                    </p>
                                    <p className="text-sm text-slate-500 capitalize">{critique.severity}</p>
                                </div>
                            </div>
                            <Chip
                                label={critique.count}
                                size="small"
                                color={getSeverityColor(critique.severity) as any}
                                sx={{ fontWeight: 600 }}
                            />
                        </motion.div>
                    ))}
                </div>
            </motion.div>

            {/* Summary */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="bg-white rounded-2xl p-6 shadow-lg border border-slate-200"
            >
                <h3 className="text-xl font-bold text-slate-900 mb-4">Summary</h3>
                <p className="text-slate-700 leading-relaxed">{summary}</p>
            </motion.div>

            {/* Strengths & Weaknesses */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Strengths */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="bg-white rounded-2xl p-6 shadow-lg border border-slate-200"
                >
                    <h3 className="text-xl font-bold text-green-600 mb-4">✅ Strengths</h3>
                    <ul className="space-y-2">
                        {strengths.map((strength, index) => (
                            <motion.li
                                key={index}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.7 + index * 0.05 }}
                                className="flex items-start gap-2 text-slate-700"
                            >
                                <span className="text-green-500 mt-1">•</span>
                                <span>{strength}</span>
                            </motion.li>
                        ))}
                    </ul>
                </motion.div>

                {/* Weaknesses */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.7 }}
                    className="bg-white rounded-2xl p-6 shadow-lg border border-slate-200"
                >
                    <h3 className="text-xl font-bold text-orange-600 mb-4">⚠️ Weaknesses</h3>
                    <ul className="space-y-2">
                        {weaknesses.map((weakness, index) => (
                            <motion.li
                                key={index}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.8 + index * 0.05 }}
                                className="flex items-start gap-2 text-slate-700"
                            >
                                <span className="text-orange-500 mt-1">•</span>
                                <span>{weakness}</span>
                            </motion.li>
                        ))}
                    </ul>
                </motion.div>
            </div>

            {/* Actions */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 }}
                className="flex flex-wrap gap-4"
            >
                <Button
                    variant="contained"
                    startIcon={<Download />}
                    sx={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        textTransform: 'none',
                        px: 3,
                        py: 1.5,
                    }}
                >
                    Download PDF Report
                </Button>
                <Button
                    variant="outlined"
                    startIcon={<Share2 />}
                    sx={{ textTransform: 'none', px: 3, py: 1.5 }}
                >
                    Share Review
                </Button>
            </motion.div>
        </motion.div>
    );
}
