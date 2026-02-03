/**
 * Main dashboard with chatbot interface.
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ChatBot from './ChatBot';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1 className="app-title">AI Email Assistant</h1>

          <div className="user-section">
            <button
              className="user-button"
              onClick={() => setShowUserMenu(!showUserMenu)}
            >
              {user?.picture ? (
                <img src={user.picture} alt={user.name} className="user-avatar" />
              ) : (
                <div className="user-avatar-placeholder">
                  {user?.name?.charAt(0) || 'U'}
                </div>
              )}
              <span className="user-name">{user?.name || 'User'}</span>
            </button>

            {showUserMenu && (
              <div className="user-menu">
                <div className="user-menu-item user-info">
                  <div className="user-email">{user?.email}</div>
                </div>
                <button className="user-menu-item logout-button" onClick={logout}>
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main content - ChatBot */}
      <main className="dashboard-main">
        <ChatBot />
      </main>
    </div>
  );
};

export default Dashboard;
