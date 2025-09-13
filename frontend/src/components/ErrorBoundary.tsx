import React from 'react'

type Props = { children: React.ReactNode; fallback?: React.ReactNode }

type State = { hasError: boolean }

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: unknown) {
    // Aquí podríamos enviar el error a un servicio
    console.error('ErrorBoundary caught', error)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? <div>Algo salió mal.</div>
    }
    return this.props.children
  }
}

