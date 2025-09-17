import { useState } from 'react'
import { GitHubUpload } from './components/GitHubUpload'
import { ChatBox } from './components/ChatBox'

function App() {
  const [projectUrl, setProjectUrl] = useState<string | undefined>(undefined)
  const [showUploadModal, setShowUploadModal] = useState(false)

  const handleUploadSuccess = (canonicalUrl: string) => {
    setProjectUrl(canonicalUrl)
    setShowUploadModal(false)
  }

  const handleUploadError = (error: string) => {
    console.error('Upload failed:', error)
  }

  const handleChatError = (error: string) => {
    console.error('Chat error:', error)
  }

  const handleRemoveProject = () => {
    setProjectUrl(undefined)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-8 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-blue-600 mb-2">AI Code Explorer</h1>
          <p className="text-gray-600 text-lg">
            Chat with AI about programming and development topics
          </p>
        </header>

        <main>
          <ChatBox
            projectUrl={projectUrl}
            onError={handleChatError}
            onAddProject={() => setShowUploadModal(true)}
            onRemoveProject={handleRemoveProject}
          />
        </main>

        {/* Simple Modal with Backdrop Blur */}
        {showUploadModal && (
          <>
            <div className="fixed inset-0 backdrop-blur-sm z-40" onClick={() => setShowUploadModal(false)} />
            <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50">
              <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 w-96 p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-2xl font-bold text-gray-900">Add GitHub Project</h3>
                  <button
                    onClick={() => setShowUploadModal(false)}
                    className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full p-2 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <GitHubUpload
                  onUploadSuccess={handleUploadSuccess}
                  onUploadError={handleUploadError}
                />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default App
