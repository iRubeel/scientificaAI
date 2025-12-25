'use client';

import { motion } from 'framer-motion';
import { Sparkles, Brain, Target, BarChart3, ArrowRight } from 'lucide-react';
import { Button } from '@mui/material';

export default function Hero() {
    return (
        <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 text-white py-20">
            {/* Animated background */}
            <div className="absolute inset-0 opacity-20">
                <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500 rounded-full filter blur-3xl animate-pulse" />
                <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500 rounded-full filter blur-3xl animate-pulse delay-1000" />
            </div>

            <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="text-center"
                >
                    {/* Gemini Pro 3 Badge */}
                    <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/20 backdrop-blur-sm border border-purple-400/30 rounded-full mb-6"
                    >
                        <Sparkles className="w-4 h-4 text-purple-300" />
                        <span className="text-sm font-medium text-purple-200">Powered by Gemini Pro 3</span>
                    </motion.div>

                    {/* Main Headline */}
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3, duration: 0.6 }}
                        className="text-5xl md:text-7xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-100 to-purple-200"
                    >
                        Rigorous AI Review for
                        <br />
                        Mathematical Research
                    </motion.h1>

                    {/* Subtitle */}
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4, duration: 0.6 }}
                        className="text-xl md:text-2xl text-blue-100 mb-12 max-w-3xl mx-auto"
                    >
                        Autonomous paper review in minutes, not months. Multi-level self-critique with transparent reasoning.
                    </motion.p>

                    {/* Feature Grid */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5, duration: 0.6 }}
                        className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12"
                    >
                        <FeatureCard
                            icon={<Brain className="w-6 h-6" />}
                            title="Multi-level Self-Critique"
                            description="8 critique categories"
                            delay={0.6}
                        />
                        <FeatureCard
                            icon={<Target className="w-6 h-6" />}
                            title="Epistemic Tracking"
                            description="Confidence & uncertainty"
                            delay={0.7}
                        />
                        <FeatureCard
                            icon={<BarChart3 className="w-6 h-6" />}
                            title="Specialized Tools"
                            description="SymPy, SciPy, arXiv"
                            delay={0.8}
                        />
                        <FeatureCard
                            icon={<Sparkles className="w-6 h-6" />}
                            title="Transparent Reasoning"
                            description="See every step"
                            delay={0.9}
                        />
                    </motion.div>

                    {/* CTA Buttons */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 1, duration: 0.6 }}
                        className="flex flex-col sm:flex-row gap-4 justify-center"
                    >
                        <Button
                            variant="contained"
                            size="large"
                            endIcon={<ArrowRight />}
                            sx={{
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                px: 4,
                                py: 1.5,
                                fontSize: '1.125rem',
                                fontWeight: 600,
                                textTransform: 'none',
                                '&:hover': {
                                    background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                                    transform: 'translateY(-2px)',
                                    boxShadow: '0 10px 40px rgba(102, 126, 234, 0.4)',
                                },
                                transition: 'all 0.3s ease',
                            }}
                            onClick={() => document.getElementById('paper-submission')?.scrollIntoView({ behavior: 'smooth' })}
                        >
                            Try Demo Paper
                        </Button>
                        <Button
                            variant="outlined"
                            size="large"
                            sx={{
                                borderColor: 'rgba(255, 255, 255, 0.3)',
                                color: 'white',
                                px: 4,
                                py: 1.5,
                                fontSize: '1.125rem',
                                fontWeight: 600,
                                textTransform: 'none',
                                '&:hover': {
                                    borderColor: 'rgba(255, 255, 255, 0.6)',
                                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                    transform: 'translateY(-2px)',
                                },
                                transition: 'all 0.3s ease',
                            }}
                            onClick={() => document.getElementById('paper-submission')?.scrollIntoView({ behavior: 'smooth' })}
                        >
                            Upload Your Paper
                        </Button>
                    </motion.div>
                </motion.div>
            </div>
        </section>
    );
}

function FeatureCard({ icon, title, description, delay }: { icon: React.ReactNode; title: string; description: string; delay: number }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay, duration: 0.6 }}
            whileHover={{ scale: 1.05, y: -5 }}
            className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 text-center hover:bg-white/15 transition-all cursor-pointer"
        >
            <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-500/20 rounded-xl mb-4">
                {icon}
            </div>
            <h3 className="text-lg font-semibold mb-2">{title}</h3>
            <p className="text-sm text-blue-200">{description}</p>
        </motion.div>
    );
}
