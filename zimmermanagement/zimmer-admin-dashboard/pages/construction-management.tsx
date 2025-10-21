import React, { useState, useEffect } from 'react'
import Layout from '../components/Layout'
import { useAuth } from '../contexts/AuthContext'

interface ConstructionEmail {
  id: number
  email: string
  submitted_at: string
}

interface ConstructionConfig {
  isUnderConstruction: boolean
}

export default function ConstructionManagement() {
  const [emails, setEmails] = useState<ConstructionEmail[]>([])
  const [config, setConfig] = useState<ConstructionConfig>({ isUnderConstruction: false })
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const { user, isAuthenticated } = useAuth()

  useEffect(() => {
    if (isAuthenticated && user?.is_admin) {
      fetchData()
    }
  }, [isAuthenticated, user])

  const fetchData = async () => {
    try {
      const [emailsResponse, configResponse] = await Promise.all([
        fetch('/api/construction/emails', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }),
        fetch('/api/admin/construction-config', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
      ])

      if (emailsResponse.ok) {
        const emailsData = await emailsResponse.json()
        setEmails(emailsData)
      }

      if (configResponse.ok) {
        const configData = await configResponse.json()
        setConfig(configData)
      }
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleConstructionMode = async () => {
    setSubmitting(true)
    try {
      const response = await fetch('/api/admin/construction-config', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          isUnderConstruction: !config.isUnderConstruction
        })
      })

      if (response.ok) {
        setConfig(prev => ({ ...prev, isUnderConstruction: !prev.isUnderConstruction }))
      } else {
        alert('Failed to update construction mode')
      }
    } catch (error) {
      console.error('Error updating construction mode:', error)
      alert('Error updating construction mode')
    } finally {
      setSubmitting(false)
    }
  }

  const deleteEmail = async (emailId: number) => {
    if (!confirm('Are you sure you want to delete this email?')) return

    try {
      const response = await fetch(`/api/construction/emails/${emailId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.ok) {
        setEmails(emails.filter(email => email.id !== emailId))
      } else {
        alert('Failed to delete email')
      }
    } catch (error) {
      console.error('Error deleting email:', error)
      alert('Error deleting email')
    }
  }

  const exportEmails = () => {
    const csvContent = [
      'Email,Submitted At',
      ...emails.map(email => `${email.email},"${new Date(email.submitted_at).toLocaleString()}"`)
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `construction-emails-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  if (!isAuthenticated || !user?.is_admin) {
    return (
      <Layout title="Access Denied">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-red-600">Access Denied</h1>
          <p>You need admin privileges to access this page.</p>
        </div>
      </Layout>
    )
  }

  if (loading) {
    return (
      <Layout title="Construction Management">
        <div className="p-6">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-4 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Construction Management">
      <div className="p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Construction Management</h1>
          <p className="text-gray-600">Manage construction mode and view submitted emails</p>
        </div>

        {/* Construction Mode Toggle */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Construction Mode</h2>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-700">
                Current status: <span className={`font-semibold ${config.isUnderConstruction ? 'text-red-600' : 'text-green-600'}`}>
                  {config.isUnderConstruction ? 'Under Construction' : 'Live'}
                </span>
              </p>
              <p className="text-sm text-gray-500 mt-1">
                {config.isUnderConstruction 
                  ? 'User panel shows construction page' 
                  : 'User panel shows normal interface'
                }
              </p>
            </div>
            <button
              onClick={toggleConstructionMode}
              disabled={submitting}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                config.isUnderConstruction
                  ? 'bg-green-600 hover:bg-green-700 text-white'
                  : 'bg-red-600 hover:bg-red-700 text-white'
              } ${submitting ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {submitting ? 'Updating...' : config.isUnderConstruction ? 'Go Live' : 'Enable Construction Mode'}
            </button>
          </div>
        </div>

        {/* Email Management */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Submitted Emails ({emails.length})</h2>
            <div className="space-x-3">
              <button
                onClick={exportEmails}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Export CSV
              </button>
              <button
                onClick={fetchData}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Refresh
              </button>
            </div>
          </div>

          {emails.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No emails submitted yet.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Submitted At
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {emails.map((email) => (
                    <tr key={email.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {email.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(email.submitted_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => deleteEmail(email.id)}
                          className="text-red-600 hover:text-red-900 transition-colors"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
