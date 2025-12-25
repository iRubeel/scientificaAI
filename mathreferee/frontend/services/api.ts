/**
 * API service for communicating with the Revly backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface AnalyzeRequest {
    arxiv_id?: string;
    pdf_file?: File;
}

export interface AnalyzeResponse {
    report_id: string;
    paper_title: string;
    recommendation: string;
    confidence: number;
    summary: string;
    strengths: string[];
    weaknesses: string[];
    claims: Array<{
        claim_id: string;
        content: string;
        claim_type: string;
        confidence: number;
        status: string;
    }>;
    issues: Array<{
        issue_id: string;
        severity: string;
        issue_type: string;
        description: string;
        location: string;
        affects_validity?: boolean;
    }>;
}

/**
 * Analyze a paper by arXiv ID
 */
export async function analyzePaper(request: AnalyzeRequest): Promise<AnalyzeResponse> {
    // Backend expects JSON body with arxiv_id field
    const body: any = {};

    if (request.arxiv_id) {
        body.arxiv_id = request.arxiv_id;
    }

    if (request.pdf_file) {
        // For now, PDF upload not supported by backend
        throw new Error('PDF upload not yet supported. Please use arXiv ID.');
    }

    const response = await fetch(`${API_BASE_URL}/review-paper`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || error.error || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    // Check if the review was successful
    if (!data.success && data.error) {
        throw new Error(data.error);
    }

    // Transform backend response to frontend format
    return {
        report_id: data.review_id,
        paper_title: data.paper_title,
        recommendation: data.recommendation || 'Pending',
        confidence: data.confidence || 0,
        summary: data.summary || '',
        strengths: data.strengths || [],
        weaknesses: data.weaknesses || [],
        claims: data.claims_analyzed || [],
        issues: data.issues_found || [],
    };
}

/**
 * Check backend health
 */
export async function checkHealth(): Promise<{ status: string; agent_initialized: boolean }> {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
}
