import { render, screen } from '@testing-library/react'
import Header from '../../components/Header'
import Footer from '../../components/Footer'

describe('Layout Components', () => {
  it('renders Header with banner role', () => {
    render(<Header />)
    const header = screen.getByRole('banner')
    expect(header).toBeInTheDocument()
  })

  it('renders Footer with contentinfo role', () => {
    render(<Footer />)
    const footer = screen.getByRole('contentinfo')
    expect(footer).toBeInTheDocument()
  })
})
