'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Sparkles,
  Brain,
  Shield,
  Zap,
  FileText,
  CheckCircle2,
  ArrowRight,
  Upload,
  Search,
  FileCheck
} from 'lucide-react';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-background via-background to-muted/20">
      {/* Hero Section - Stunning gradient with animations */}
      <section className="relative overflow-hidden">
        {/* Animated background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-brand-600/10 via-purple-600/10 to-pink-600/10" />

        {/* Floating orbs animation */}
        <div className="absolute inset-0 overflow-hidden">
          <motion.div
            className="absolute top-20 left-10 w-72 h-72 bg-brand-500/20 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <motion.div
            className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"
            animate={{
              scale: [1.2, 1, 1.2],
              opacity: [0.2, 0.4, 0.2],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        </div>

        <div className="container relative max-w-7xl mx-auto px-4 py-24 md:py-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-4xl mx-auto text-center space-y-8"
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-500/10 border border-brand-500/20 backdrop-blur-sm"
            >
              <Sparkles className="h-4 w-4 text-brand-600" />
              <span className="text-sm font-medium text-brand-700 dark:text-brand-300">
                Powered by Gemini Pro 3
              </span>
            </motion.div>

            {/* Main Headline */}
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
              <span className="gradient-text">
                Autonomous AI Referee
              </span>
              <br />
              <span className="text-foreground">
                for Mathematical Research
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              Rigorous peer review with transparent epistemic tracking and multi-level critique.
              Built for researchers who demand <span className="text-foreground font-semibold">precision</span>.
            </p>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 justify-center pt-4"
            >
              <Button asChild size="xl" variant="gradient" className="group">
                <Link href="/upload" className="flex items-center gap-2">
                  Upload Paper
                  <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="xl">
                <Link href="/sample">View Sample Review</Link>
              </Button>
            </motion.div>

            {/* Trust indicators */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="flex items-center justify-center gap-8 pt-8 text-sm text-muted-foreground"
            >
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-success" />
                <span>Free to use</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-success" />
                <span>No signup required</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-success" />
                <span>Instant results</span>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How It Works - Modern 3-step process */}
      <section className="container max-w-7xl mx-auto px-4 py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">How It Works</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Three simple steps to get comprehensive AI-powered peer review
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {/* Connection lines */}
          <div className="hidden md:block absolute top-24 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-border to-transparent" />

          <ProcessCard
            icon={Upload}
            number="01"
            title="Upload Paper"
            description="Submit your paper via PDF upload or arXiv link. Our system instantly parses mathematical content and extracts key claims."
            delay={0.1}
          />
          <ProcessCard
            icon={Search}
            number="02"
            title="AI Analysis"
            description="Advanced validation using symbolic mathematics, statistical tools, and academic databases with real-time confidence tracking."
            delay={0.2}
          />
          <ProcessCard
            icon={FileCheck}
            number="03"
            title="Get Review"
            description="Receive a comprehensive referee report with identified issues, severity classifications, and transparent reasoning chains."
            delay={0.3}
          />
        </div>
      </section>

      {/* Key Features - Glass morphism cards */}
      <section className="container max-w-7xl mx-auto px-4 py-24 bg-gradient-to-b from-transparent to-muted/30">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">Powered by Advanced AI</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Cutting-edge technology for rigorous mathematical validation
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <FeatureCard
            icon={Brain}
            title="Multi-Level Critique"
            description="8 specialized critique categories including logical gaps, circular reasoning, and statistical errors."
            delay={0.1}
          />
          <FeatureCard
            icon={Shield}
            title="Epistemic Tracking"
            description="Dynamic confidence scores that evolve as new evidence emerges during analysis."
            delay={0.2}
          />
          <FeatureCard
            icon={Zap}
            title="Specialized Tools"
            description="Integration with SymPy, SciPy, arXiv, and Semantic Scholar for comprehensive validation."
            delay={0.3}
          />
          <FeatureCard
            icon={FileText}
            title="Transparent Reasoning"
            description="Every critique includes detailed reasoning chains showing how conclusions were reached."
            delay={0.4}
          />
        </div>
      </section>

      {/* Methodology Section - Accordion style */}
      <section className="container max-w-5xl mx-auto px-4 py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">Our Methodology</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            A rigorous, transparent approach to AI-powered peer review
          </p>
        </motion.div>

        <div className="space-y-4">
          <MethodologyCard
            number="1"
            title="Claim Extraction"
            description="Identifies mathematical assertions, theorems, lemmas, and statistical claims. Each claim is cataloged with location, dependencies, and type classification."
            delay={0.1}
          />
          <MethodologyCard
            number="2"
            title="Mathematical Validation"
            description="Claims validated using symbolic mathematics (SymPy), statistical analysis (SciPy), and literature search (arXiv, Semantic Scholar) for contextual verification."
            delay={0.2}
          />
          <MethodologyCard
            number="3"
            title="Epistemic Confidence"
            description="Each claim receives a confidence score based on evidence quality and validation results. Confidence dynamically adjusts as new information emerges."
            delay={0.3}
          />
          <MethodologyCard
            number="4"
            title="Self-Critique System"
            description="Employs 8 critique categories with severity classification. Each critique includes suggested resolutions and transparent reasoning."
            delay={0.4}
          />
        </div>
      </section>

      {/* Final CTA */}
      <section className="container max-w-4xl mx-auto px-4 py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="glass rounded-3xl p-12 text-center space-y-6"
        >
          <h2 className="text-4xl md:text-5xl font-bold">
            Ready to elevate your research?
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Get instant, comprehensive AI-powered peer review for your mathematical or statistical research paper.
          </p>
          <Button asChild size="xl" variant="gradient" className="group">
            <Link href="/upload" className="flex items-center gap-2">
              Start Free Review
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </Button>
        </motion.div>
      </section>
    </div>
  );
}

// Process Card Component
function ProcessCard({
  icon: Icon,
  number,
  title,
  description,
  delay
}: {
  icon: any;
  number: string;
  title: string;
  description: string;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay }}
      className="relative"
    >
      <Card hover className="h-full border-2 hover:border-brand-500/50 transition-all duration-300">
        <CardHeader className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-500 to-purple-600 text-white shadow-lg">
              <Icon className="h-8 w-8" />
            </div>
            <span className="text-6xl font-bold text-muted/20">{number}</span>
          </div>
          <CardTitle className="text-2xl">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <CardDescription className="text-base leading-relaxed">
            {description}
          </CardDescription>
        </CardContent>
      </Card>
    </motion.div>
  );
}

// Feature Card Component
function FeatureCard({
  icon: Icon,
  title,
  description,
  delay
}: {
  icon: any;
  title: string;
  description: string;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay }}
    >
      <Card hover className="h-full glass border-2 hover:border-brand-500/30 transition-all duration-300">
        <CardHeader className="space-y-4">
          <div className="flex items-center justify-center w-14 h-14 rounded-xl bg-brand-500/10 text-brand-600">
            <Icon className="h-7 w-7" />
          </div>
          <CardTitle className="text-xl">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <CardDescription className="text-sm leading-relaxed">
            {description}
          </CardDescription>
        </CardContent>
      </Card>
    </motion.div>
  );
}

// Methodology Card Component
function MethodologyCard({
  number,
  title,
  description,
  delay
}: {
  number: string;
  title: string;
  description: string;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay }}
    >
      <Card className="border-l-4 border-l-brand-500 hover:shadow-lg transition-all duration-300">
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="flex items-center justify-center w-10 h-10 rounded-full bg-brand-500 text-white font-bold">
              {number}
            </div>
            <CardTitle className="text-xl">{title}</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <CardDescription className="text-base leading-relaxed pl-14">
            {description}
          </CardDescription>
        </CardContent>
      </Card>
    </motion.div>
  );
}
