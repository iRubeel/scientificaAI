'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Upload, FileText, CheckCircle2, Circle } from 'lucide-react';

interface AnalysisStep {
    id: string;
    label: string;
    status: 'pending' | 'active' | 'complete';
}

export default function UploadPage() {
    const [arxivId, setArxivId] = useState('');
    const [file, setFile] = useState<File | null>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const [steps, setSteps] = useState<AnalysisStep[]>([
        { id: '1', label: 'Document parsed', status: 'pending' },
        { id: '2', label: 'Claims extracted', status: 'pending' },
        { id: '3', label: 'Mathematical validation', status: 'pending' },
        { id: '4', label: 'Statistical review', status: 'pending' },
        { id: '5', label: 'Epistemic tracking', status: 'pending' },
        { id: '6', label: 'Report generation', status: 'pending' },
    ]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setError(null);
        }
    };

    const handleSubmit = async () => {
        if (!arxivId && !file) {
            setError('Please provide either an arXiv ID or upload a PDF file.');
            return;
        }

        setIsAnalyzing(true);
        setError(null);

        // Simulate analysis progress
        // In production, this would call the actual API
        simulateAnalysis();
    };

    const simulateAnalysis = () => {
        let currentStep = 0;
        const interval = setInterval(() => {
            currentStep++;
            if (currentStep <= steps.length) {
                setSteps(prev => prev.map((step, idx) => ({
                    ...step,
                    status: idx < currentStep - 1 ? 'complete' : idx === currentStep - 1 ? 'active' : 'pending'
                })));
                setProgress((currentStep / steps.length) * 100);
            } else {
                clearInterval(interval);
                // Redirect to results page
                setTimeout(() => {
                    window.location.href = '/review/sample';
                }, 1000);
            }
        }, 2000);
    };

    return (
        <div className="container max-w-screen-lg mx-auto px-4 py-12">
            <div className="max-w-2xl mx-auto space-y-8">
                <div className="space-y-2">
                    <h1 className="text-3xl font-semibold tracking-tight">Submit Paper for Review</h1>
                    <p className="text-muted-foreground">
                        Upload your paper or provide an arXiv link to begin the autonomous review process.
                    </p>
                </div>

                {!isAnalyzing ? (
                    <Card>
                        <CardHeader>
                            <CardTitle>Paper Submission</CardTitle>
                            <CardDescription>
                                Supported formats: PDF files or arXiv identifiers
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* File Upload */}
                            <div className="space-y-2">
                                <Label htmlFor="file-upload">Upload PDF</Label>
                                <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors cursor-pointer">
                                    <input
                                        id="file-upload"
                                        type="file"
                                        accept=".pdf"
                                        onChange={handleFileChange}
                                        className="hidden"
                                    />
                                    <label htmlFor="file-upload" className="cursor-pointer">
                                        {file ? (
                                            <div className="flex items-center justify-center gap-2 text-foreground">
                                                <FileText className="w-5 h-5" />
                                                <span className="font-medium">{file.name}</span>
                                            </div>
                                        ) : (
                                            <div className="space-y-2">
                                                <Upload className="w-8 h-8 mx-auto text-muted-foreground" />
                                                <div className="text-sm text-muted-foreground">
                                                    Drop PDF here or click to browse
                                                </div>
                                            </div>
                                        )}
                                    </label>
                                </div>
                            </div>

                            <div className="relative">
                                <div className="absolute inset-0 flex items-center">
                                    <Separator />
                                </div>
                                <div className="relative flex justify-center text-xs uppercase">
                                    <span className="bg-card px-2 text-muted-foreground">Or</span>
                                </div>
                            </div>

                            {/* arXiv ID */}
                            <div className="space-y-2">
                                <Label htmlFor="arxiv-id">arXiv ID</Label>
                                <Input
                                    id="arxiv-id"
                                    placeholder="e.g., 2301.12345"
                                    value={arxivId}
                                    onChange={(e) => setArxivId(e.target.value)}
                                />
                                <p className="text-xs text-muted-foreground">
                                    Enter the arXiv identifier to fetch the paper directly
                                </p>
                            </div>

                            {error && (
                                <Alert variant="destructive">
                                    <AlertDescription>{error}</AlertDescription>
                                </Alert>
                            )}

                            <Button
                                onClick={handleSubmit}
                                className="w-full"
                                size="lg"
                                disabled={!arxivId && !file}
                            >
                                Submit for Review
                            </Button>
                        </CardContent>
                    </Card>
                ) : (
                    <Card>
                        <CardHeader>
                            <CardTitle>Analyzing Paper</CardTitle>
                            <CardDescription>
                                The review process typically takes 2-5 minutes
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Progress Steps */}
                            <div className="space-y-3">
                                {steps.map((step) => (
                                    <div key={step.id} className="flex items-center gap-3">
                                        <div className="flex-shrink-0">
                                            {step.status === 'complete' ? (
                                                <CheckCircle2 className="w-5 h-5 text-primary" />
                                            ) : step.status === 'active' ? (
                                                <div className="w-5 h-5 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                                            ) : (
                                                <Circle className="w-5 h-5 text-muted" />
                                            )}
                                        </div>
                                        <span className={`text-sm ${step.status === 'complete' ? 'text-foreground' :
                                                step.status === 'active' ? 'text-foreground font-medium' :
                                                    'text-muted-foreground'
                                            }`}>
                                            {step.label}
                                        </span>
                                    </div>
                                ))}
                            </div>

                            {/* Progress Bar */}
                            <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-muted-foreground">Progress</span>
                                    <span className="font-medium">{Math.round(progress)}%</span>
                                </div>
                                <Progress value={progress} className="h-2" />
                            </div>

                            <p className="text-sm text-muted-foreground text-center">
                                Estimated time remaining: {Math.max(0, Math.ceil((100 - progress) / 20))} minutes
                            </p>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
