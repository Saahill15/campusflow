import React from 'react'

export default class ErrorBoundary extends React.Component<any, { hasError: boolean }> {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError() {
    return { hasError: true }
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8">
          <h2 className="text-xl font-semibold">Something went wrong</h2>
        </div>
      )
    }
    return this.props.children
  }
}
