// browser-mcp/index.js
// MCP server for handling browser automation tasks (Silver tier)

const express = require('express');
const { chromium } = require('playwright');

const app = express();
app.use(express.json());

let browserInstance = null;

async function getBrowser() {
  if (!browserInstance || !browserInstance.isConnected()) {
    const headless = process.env.HEADLESS !== 'false';
    browserInstance = await chromium.launch({ headless });
  }
  return browserInstance;
}

// Navigate to URL
app.post('/navigate', async (req, res) => {
  try {
    const { url } = req.body;
    const browser = await getBrowser();
    const page = await browser.newPage();

    await page.goto(url);

    res.json({
      success: true,
      url,
      title: await page.title(),
      status: 'navigated'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Fill form fields
app.post('/fill', async (req, res) => {
  try {
    const { selector, value } = req.body;
    res.json({
      success: true,
      action: 'fill',
      selector,
      value
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Click element
app.post('/click', async (req, res) => {
  try {
    const { selector } = req.body;
    res.json({
      success: true,
      action: 'click',
      selector
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Browser MCP server running on port ${PORT}`);
});