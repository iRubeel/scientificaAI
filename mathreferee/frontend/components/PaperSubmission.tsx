'use client';

import { useState } from 'react';
import { Box, TextField, Button, Typography, Paper, Divider, CircularProgress, Alert } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { analyzePaper } from '../services/api';
import { Review } from '../types/review';

interface Props {
  onAnalyze?: (review: Review) => void;
  onAnalyzeStart?: () => void;
}

export default function PaperSubmission({ onAnalyze, onAnalyzeStart }: Props) {
  const [arxivId, setArxivId] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);

    // Trigger analysis start callback
    if (onAnalyzeStart) {
      onAnalyzeStart();
    }

    try {
      console.log('Analyzing paper:', arxivId || file?.name);

      const response = await analyzePaper({
        arxiv_id: arxivId || undefined,
        pdf_file: file || undefined,
      });

      console.log('Analysis complete:', response);

      if (onAnalyze) {
        // Transform backend response to frontend Review format
        onAnalyze({
          recommendation: response.recommendation,
          confidence: response.confidence,
          sections: [
            {
              title: "Summary",
              content: response.summary,
              claims: []
            },
            {
              title: "Strengths",
              content: response.strengths.join('\n• '),
              claims: []
            },
            {
              title: "Weaknesses",
              content: response.weaknesses.join('\n• '),
              claims: []
            },
            {
              title: "Issues Found",
              content: response.issues.map(issue =>
                `**[${issue.severity.toUpperCase()}] ${issue.issue_type}**\n${issue.description}`
              ).join('\n\n'),
              claims: []
            }
          ]
        });
      }
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err instanceof Error ? err.message : 'Failed to analyze paper');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Analyze Paper
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box component="form" noValidate autoComplete="off" sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <TextField
          label="arXiv ID"
          variant="outlined"
          value={arxivId}
          onChange={(e) => setArxivId(e.target.value)}
          placeholder="e.g., 2301.12345"
          fullWidth
          disabled={loading}
        />

        <Divider>OR</Divider>

        <Button
          component="label"
          variant="outlined"
          startIcon={<CloudUploadIcon />}
          sx={{ height: 56 }}
          disabled={loading}
        >
          {file ? file.name : "Upload PDF"}
          <input
            type="file"
            hidden
            accept=".pdf"
            onChange={handleFileChange}
            aria-label="Upload PDF"
          />
        </Button>

        <Button
          variant="contained"
          size="large"
          onClick={handleAnalyze}
          disabled={(!arxivId && !file) || loading}
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
        >
          {loading ? 'Analyzing...' : 'Analyze'}
        </Button>
      </Box>
    </Paper>
  );
}
