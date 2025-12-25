import { render, screen } from '@testing-library/react'
import ReviewDisplay from '../../components/ReviewDisplay'
import { Review } from '../../types/review'

const mockReview: Review = {
  recommendation: "Accept",
  confidence: 0.9,
  sections: [
    {
      title: "Introduction",
      content: "Intro content",
      claims: []
    }
  ]
}

describe('ReviewDisplay Component', () => {
  it('renders review details', () => {
    render(<ReviewDisplay review={mockReview} />)
    // Using regex to match flexible formatting
    expect(screen.getByText(/Accept/i)).toBeInTheDocument()
    expect(screen.getByText(/0.9/i)).toBeInTheDocument()
    expect(screen.getByText("Introduction")).toBeInTheDocument()
  })

  it('renders sections as accordions', () => {
    render(<ReviewDisplay review={mockReview} />)
    // Accordion summary should act as a button
    expect(screen.getByRole('button', { name: /Introduction/i })).toBeInTheDocument()
  })
})
