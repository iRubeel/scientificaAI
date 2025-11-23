"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, Loader2, CheckCircle, AlertCircle, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";

interface ParsedResult {
    theoremMarkdown: string;
}

export default function UploadZone() {
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<ParsedResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            setFile(acceptedFiles[0]);
            setError(null);
            setResult(null);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            "application/pdf": [".pdf"],
        },
        maxFiles: 1,
    });

    const handleUpload = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);
        setResult(null); // Clear previous results

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("/api/parse-pdf", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Failed to parse PDF");
            }

            const data = await response.json();
            setResult(data);
        } catch (err) {
            setError("An error occurred while processing the file. Please try again.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto space-y-8">
            <Card className="border-dashed border-2 border-muted-foreground/25 bg-muted/5 hover:bg-muted/10 transition-colors">
                <CardContent className="p-0">
                    <div
                        {...getRootProps()}
                        className={cn(
                            "flex flex-col items-center justify-center p-12 text-center cursor-pointer transition-all duration-300",
                            isDragActive ? "scale-[0.99] bg-muted/20" : ""
                        )}
                    >
                        <input {...getInputProps()} />
                        <div className="p-4 rounded-full bg-primary/10 mb-4 transition-transform duration-300 hover:scale-110">
                            <Upload className="w-8 h-8 text-primary" />
                        </div>
                        <h3 className="text-lg font-semibold mb-2">
                            {file ? file.name : "Drop your research paper here"}
                        </h3>
                        <p className="text-sm text-muted-foreground max-w-xs mx-auto">
                            {file
                                ? "Ready to analyze. Click the button below."
                                : "Drag & drop a PDF, or click to select"}
                        </p>
                    </div>
                </CardContent>
            </Card>

            <div className="flex justify-center">
                <Button
                    size="lg"
                    onClick={handleUpload}
                    disabled={!file || loading}
                    className="min-w-[180px] text-base font-medium shadow-lg shadow-primary/20 transition-all hover:shadow-primary/40"
                >
                    {loading ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Extracting Truth...
                        </>
                    ) : (
                        <>
                            <Sparkles className="mr-2 h-4 w-4" />
                            Analyze Paper
                        </>
                    )}
                </Button>
            </div>

            {error && (
                <div className="p-4 rounded-lg bg-destructive/10 text-destructive flex items-center gap-3 animate-in fade-in slide-in-from-top-2">
                    <AlertCircle className="w-5 h-5" />
                    <p>{error}</p>
                </div>
            )}

            {result && (
                <div className="animate-in fade-in slide-in-from-bottom-8 duration-700 fill-mode-forwards">
                    <div className="flex items-center gap-2 text-green-500 mb-6 justify-center">
                        <CheckCircle className="w-5 h-5" />
                        <span className="font-medium">Extraction Complete</span>
                    </div>

                    <Card className="overflow-hidden border-primary/20 bg-card/50 backdrop-blur-sm shadow-2xl">
                        <CardHeader className="bg-primary/5 border-b border-primary/10 pb-4">
                            <CardTitle className="flex items-center gap-2 text-xl">
                                <FileText className="w-5 h-5 text-primary" />
                                Extracted Theorem + Proof
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-8 prose prose-invert max-w-none prose-headings:text-primary prose-strong:text-foreground prose-p:text-muted-foreground prose-li:text-muted-foreground">
                            <ReactMarkdown>{result.theoremMarkdown}</ReactMarkdown>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
}
