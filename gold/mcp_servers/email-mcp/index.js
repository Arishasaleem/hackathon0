// email-mcp/index.js
// MCP server for handling email operations

const express = require('express');
const nodemailer = require('nodemailer');
require('dotenv').config();

const app = express();
app.use(express.json());

// Email transporter configuration
const transporter = nodemailer.createTransporter({
  host: process.env.SMTP_HOST || 'smtp.gmail.com',
  port: parseInt(process.env.SMTP_PORT) || 587,
  secure: false,
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

// MCP endpoints
app.post('/send-email', async (req, res) => {
  try {
    const { to, subject, body, attachments } = req.body;

    const mailOptions = {
      from: process.env.EMAIL_USER,
      to,
      subject,
      text: body,
      attachments: attachments || []
    };

    const info = await transporter.sendMail(mailOptions);

    res.json({
      success: true,
      messageId: info.messageId,
      response: info.response
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.post('/draft-email', async (req, res) => {
  try {
    // Just validate and return draft info without sending
    const { to, subject, body } = req.body;

    res.json({
      success: true,
      draft: {
        to,
        subject,
        body,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.post('/search-emails', async (req, res) => {
  try {
    // This would integrate with Gmail API in a real implementation
    const { query, dateRange } = req.body;

    // Placeholder response
    res.json({
      success: true,
      emails: [],
      count: 0
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Email MCP server running on port ${PORT}`);
});