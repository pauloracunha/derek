import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import Legend from '../../src/components/Legend'

describe('Legend', () => {
  it('renderiza sem depender de nenhum lugar selecionado', () => {
    render(<Legend />)
    expect(screen.getByLabelText('Legenda')).toBeInTheDocument()
    expect(screen.getByText(/proporcionais à probabilidade relativa/)).toBeInTheDocument()
  })
})
