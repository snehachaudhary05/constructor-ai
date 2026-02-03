/**
 * ChatBot component for email assistant interface.
 */

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { chatbotAPI, emailAPI } from '../services/api';

const ChatBot = () => {
  const { sessionId } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentEmails, setCurrentEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [generatedReply, setGeneratedReply] = useState(null);
  const [showConfirmDelete, setShowConfirmDelete] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load welcome message
    const loadWelcome = async () => {
      try {
        const response = await chatbotAPI.getWelcomeMessage(sessionId);
        setMessages([
          {
            role: 'assistant',
            content: response.message,
            timestamp: new Date(),
          },
        ]);
      } catch (err) {
        console.error('Failed to load welcome message:', err);
        setMessages([
          {
            role: 'assistant',
            content: 'Hello! I\'m your AI email assistant. How can I help you today?',
            timestamp: new Date(),
          },
        ]);
      }
    };

    if (sessionId) {
      loadWelcome();
    }
  }, [sessionId]);

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');

    // Add user message to chat
    const newUserMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await chatbotAPI.sendMessage(sessionId, userMessage);

      // Add assistant response
      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        action: response.action,
        data: response.data,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Handle specific actions
      if (response.action === 'show_emails' && response.data?.emails) {
        setCurrentEmails(response.data.emails);
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date(),
          error: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateReply = async (email) => {
    setIsLoading(true);
    setSelectedEmail(email);

    try {
      const response = await emailAPI.generateReply(sessionId, email.id);
      setGeneratedReply(response);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Here's a suggested reply for the email from ${response.sender}:`,
          timestamp: new Date(),
          replyData: response,
        },
      ]);
    } catch (err) {
      console.error('Failed to generate reply:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I failed to generate a reply. Please try again.',
          timestamp: new Date(),
          error: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendReply = async () => {
    if (!generatedReply) return;

    setIsLoading(true);

    try {
      await emailAPI.sendReply(
        sessionId,
        generatedReply.email_id,
        generatedReply.proposed_reply,
        generatedReply.subject
      );

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '✅ Reply sent successfully!',
          timestamp: new Date(),
          success: true,
        },
      ]);

      setGeneratedReply(null);
      setSelectedEmail(null);
    } catch (err) {
      console.error('Failed to send reply:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '❌ Failed to send reply. Please try again.',
          timestamp: new Date(),
          error: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteEmail = async (email) => {
    setShowConfirmDelete(email);
  };

  const confirmDelete = async () => {
    if (!showConfirmDelete) return;

    setIsLoading(true);

    try {
      await emailAPI.deleteEmail(sessionId, showConfirmDelete.id);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `✅ Email "${showConfirmDelete.subject}" has been deleted.`,
          timestamp: new Date(),
          success: true,
        },
      ]);

      // Remove from current emails list
      setCurrentEmails((prev) => prev.filter((e) => e.id !== showConfirmDelete.id));
      setShowConfirmDelete(null);
    } catch (err) {
      console.error('Failed to delete email:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '❌ Failed to delete email. Please try again.',
          timestamp: new Date(),
          error: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message message-${msg.role}`}>
            <div className="message-content">
              <div className="message-text">{msg.content}</div>

              {/* Display emails if available */}
              {msg.action === 'show_emails' && msg.data?.emails && (
                <div className="emails-list">
                  {msg.data.emails.map((email, emailIdx) => (
                    <div key={emailIdx} className="email-card">
                      <div className="email-header">
                        <div className="email-sender">
                          <strong>{email.sender}</strong>
                          <span className="email-address">{email.sender_email}</span>
                        </div>
                        <span className="email-date">{email.date}</span>
                      </div>

                      <div className="email-subject">{email.subject}</div>

                      <div className="email-summary">
                        <strong>Summary:</strong> {email.summary}
                      </div>

                      <div className="email-actions">
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => handleGenerateReply(email)}
                          disabled={isLoading}
                        >
                          Reply
                        </button>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDeleteEmail(email)}
                          disabled={isLoading}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Display generated reply */}
              {msg.replyData && (
                <div className="reply-card">
                  <div className="reply-header">
                    <strong>Proposed Reply:</strong>
                  </div>
                  <div className="reply-text">{msg.replyData.proposed_reply}</div>
                  <div className="reply-actions">
                    <button
                      className="btn btn-success"
                      onClick={handleSendReply}
                      disabled={isLoading}
                    >
                      Send Reply
                    </button>
                    <button
                      className="btn btn-secondary"
                      onClick={() => setGeneratedReply(null)}
                      disabled={isLoading}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>

            <div className="message-time">
              {msg.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message message-assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          className="chat-input"
          placeholder="Type a message... (e.g., 'Show me my last 5 emails')"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          disabled={isLoading}
        />
        <button type="submit" className="send-button" disabled={isLoading || !inputMessage.trim()}>
          Send
        </button>
      </form>

      {/* Delete confirmation modal */}
      {showConfirmDelete && (
        <div className="modal-overlay" onClick={() => setShowConfirmDelete(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Confirm Delete</h3>
            <p>Are you sure you want to delete this email?</p>
            <p className="email-subject-preview">
              <strong>Subject:</strong> {showConfirmDelete.subject}
            </p>
            <div className="modal-actions">
              <button className="btn btn-danger" onClick={confirmDelete} disabled={isLoading}>
                Yes, Delete
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => setShowConfirmDelete(null)}
                disabled={isLoading}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatBot;
