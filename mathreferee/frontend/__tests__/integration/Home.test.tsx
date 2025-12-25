import { render, screen, fireEvent } from '@testing-library/react'
import Home from '../../app/page'

describe('Home Integration', () => {
  it('displays review after submission', () => {
    render(<Home />)
    
    // Fill input
    const input = screen.getByLabelText(/arxiv id/i)
    fireEvent.change(input, { target: { value: '2301.12345' } })
    
    // Click analyze
    const button = screen.getByRole('button', { name: /analyze/i })
    fireEvent.click(button)
    
    // Check for review display (mocked response)
    expect(screen.getByText(/Minor Revision/i)).toBeInTheDocument()
    expect(screen.getByText(/Abstract Analysis/i)).toBeInTheDocument()
  })
})
