import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { adminAPI, tokenAdjustmentAPI } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

interface UserAutomation {
  id: number;
  user_id: number;
  automation_id: number;
  status: string;
  created_at: string;
  user_name?: string;
  automation_name?: string;
  tokens_remaining?: number;
}

interface TokenAdjustment {
  id: number;
  user_id: number;
  amount: number;
  reason: string;
  created_at: string;
  created_by_name?: string;
}

export default function UserAutomations() {
  const [userAutomations, setUserAutomations] = useState<UserAutomation[]>([]);
  const [tokenAdjustments, setTokenAdjustments] = useState<TokenAdjustment[]>([]);
  const [loading, setLoading] = useState(true);
  const [adjustingTokens, setAdjustingTokens] = useState(false);
  const [selectedUserAutomation, setSelectedUserAutomation] = useState<UserAutomation | null>(null);
  const [adjustmentAmount, setAdjustmentAmount] = useState('');
  const [adjustmentReason, setAdjustmentReason] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchUserAutomations();
      fetchTokenAdjustments();
    }
  }, [user]);

  const fetchUserAutomations = async () => {
    try {
      setLoading(true);
      // Get all user automations - we'll filter by user if needed
      const data = await adminAPI.getUserAutomations('all', {});
      setUserAutomations(data.user_automations || []);
    } catch (error) {
      console.error('Error fetching user automations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTokenAdjustments = async () => {
    try {
      const data = await tokenAdjustmentAPI.listAdjustments();
      setTokenAdjustments(data.adjustments || []);
    } catch (error) {
      console.error('Error fetching token adjustments:', error);
    }
  };

  const handleAdjustTokens = async () => {
    if (!selectedUserAutomation || !adjustmentAmount || !adjustmentReason) return;

    setAdjustingTokens(true);
    try {
      await tokenAdjustmentAPI.adjustTokens({
        user_automation_id: selectedUserAutomation.id,
        amount: parseInt(adjustmentAmount),
        reason: adjustmentReason
      });
      
      // Refresh data
      fetchUserAutomations();
      fetchTokenAdjustments();
      
      // Reset form
      setSelectedUserAutomation(null);
      setAdjustmentAmount('');
      setAdjustmentReason('');
    } catch (error) {
      console.error('Error adjusting tokens:', error);
    } finally {
      setAdjustingTokens(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-red-100 text-red-800';
      case 'suspended': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <Layout title="User Automations">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading user automations...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="User Automations">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">User Automations</h1>
          <button
            onClick={() => {
              setSelectedUserAutomation({} as UserAutomation);
              setAdjustmentAmount('');
              setAdjustmentReason('');
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Adjust Tokens
          </button>
        </div>

        {/* User Automations Table */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">User Automations</h2>
            {userAutomations.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-gray-500 text-lg">No user automations found</div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Automation
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tokens Remaining
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Created
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {userAutomations.map((userAutomation) => (
                      <tr key={userAutomation.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {userAutomation.user_name || `User ${userAutomation.user_id}`}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {userAutomation.automation_name || `Automation ${userAutomation.automation_id}`}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(userAutomation.status)}`}>
                            {userAutomation.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {userAutomation.tokens_remaining || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(userAutomation.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button
                            onClick={() => setSelectedUserAutomation(userAutomation)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Adjust Tokens
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

        {/* Token Adjustments Table */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Token Adjustments</h2>
            {tokenAdjustments.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-gray-500 text-lg">No token adjustments found</div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Reason
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Created By
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {tokenAdjustments.map((adjustment) => (
                      <tr key={adjustment.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {adjustment.user_id}
                        </td>
                        <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${adjustment.amount > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {adjustment.amount > 0 ? '+' : ''}{adjustment.amount}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                          {adjustment.reason}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {adjustment.created_by_name || 'System'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(adjustment.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Adjust Tokens Modal */}
        {selectedUserAutomation && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Adjust Tokens</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      User Automation ID
                    </label>
                    <input
                      type="number"
                      value={selectedUserAutomation.id || ''}
                      onChange={(e) => setSelectedUserAutomation({...selectedUserAutomation, id: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Amount (positive to add, negative to subtract)
                    </label>
                    <input
                      type="number"
                      value={adjustmentAmount}
                      onChange={(e) => setAdjustmentAmount(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Reason
                    </label>
                    <textarea
                      value={adjustmentReason}
                      onChange={(e) => setAdjustmentReason(e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    onClick={() => setSelectedUserAutomation(null)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAdjustTokens}
                    disabled={adjustingTokens || !selectedUserAutomation.id || !adjustmentAmount || !adjustmentReason}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {adjustingTokens ? 'Adjusting...' : 'Adjust Tokens'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
