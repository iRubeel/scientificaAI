import { Review } from '../types/review';
import { Card, CardContent, Typography, Chip, Box, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

interface Props {
  review: Review | null;
}

export default function ReviewDisplay({ review }: Props) {
  if (!review) return null;

  return (
    <Card variant="outlined" sx={{ mt: 4 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Review Result
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Chip label={`Recommendation: ${review.recommendation}`} color="primary" />
          <Chip label={`Confidence: ${review.confidence}`} variant="outlined" />
        </Box>

        <Box>
          {review.sections.map((section, index) => (
            <Accordion key={index} defaultExpanded>
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls={`panel${index}-content`}
                id={`panel${index}-header`}
              >
                <Typography variant="h6">{section.title}</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body1">{section.content}</Typography>
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
}
