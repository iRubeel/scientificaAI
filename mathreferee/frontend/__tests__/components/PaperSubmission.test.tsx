import { render, screen, fireEvent } from '@testing-library/react'
import PaperSubmission from '../../components/PaperSubmission'

describe('PaperSubmission Component', () => {
  it('renders submission form elements', () => {
    render(<PaperSubmission />)
    expect(screen.getByLabelText(/arxiv id/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/upload pdf/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze/i })).toBeInTheDocument()
  })
})
