import { render, screen } from '@testing-library/react'
import ToolsList from '../../components/ToolsList'

const mockTools = [
  { id: '1', name: 'Calculator', description: 'Basic calc' },
  { id: '2', name: 'SymPy', description: 'Symbolic math' }
]

describe('ToolsList Component', () => {
  it('renders list of tools', () => {
    render(<ToolsList tools={mockTools} />)
    expect(screen.getByText('Calculator')).toBeInTheDocument()
    expect(screen.getByText('SymPy')).toBeInTheDocument()
  })
})
