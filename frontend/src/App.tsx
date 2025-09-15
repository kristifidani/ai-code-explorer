import { GitHubUpload } from './components/GitHubUpload'

function App() {
  const handleUploadSuccess = (canonicalUrl: string) => {
    console.log('Project uploaded successfully:', canonicalUrl)
    // TODO: Store canonical URL for use in chat/questions component
  }

  const handleUploadError = (error: string) => {
    console.error('Upload failed:', error)
    // TODO: Show error notification or toast
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-8 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-blue-600 mb-2">AI Code Explorer</h1>
          <p className="text-gray-600 text-lg">Upload a GitHub repository and ask AI-powered questions about the code</p>
        </header>

        <main>
          <GitHubUpload
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </main>
      </div>
    </div>
  )
}

export default App
