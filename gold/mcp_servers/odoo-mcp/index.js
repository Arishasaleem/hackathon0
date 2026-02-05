// odoo-mcp/index.js
// MCP server for handling Odoo ERP operations

const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

// Odoo API client configuration
class OdooClient {
  constructor() {
    this.url = process.env.ODOO_SERVER_URL;
    this.db = process.env.ODOO_DATABASE;
    this.username = process.env.ODOO_USERNAME;
    this.password = process.env.ODOO_PASSWORD;
    this.uid = null;
  }

  async authenticate() {
    if (this.uid) return this.uid;

    try {
      const response = await axios.post(`${this.url}/jsonrpc`, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          service: 'common',
          method: 'authenticate',
          args: [this.db, this.username, this.password, {}]
        },
        id: Math.floor(Math.random() * 1000)
      });

      this.uid = response.data.result;
      return this.uid;
    } catch (error) {
      throw new Error(`Authentication failed: ${error.message}`);
    }
  }

  async call_kw(model, method, args = [], kwargs = {}) {
    const uid = await this.authenticate();

    try {
      const response = await axios.post(`${this.url}/jsonrpc`, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          service: 'object',
          method: 'execute_kw',
          args: [this.db, uid, this.password, model, method, args, kwargs]
        },
        id: Math.floor(Math.random() * 1000)
      });

      return response.data.result;
    } catch (error) {
      throw new Error(`API call failed: ${error.message}`);
    }
  }
}

const odooClient = new OdooClient();

// Create invoice
app.post('/create-invoice', async (req, res) => {
  try {
    const { partner_id, lines, date } = req.body;

    const invoiceId = await odooClient.call_kw('account.move', 'create', [{
      move_type: 'out_invoice',
      partner_id,
      invoice_line_ids: lines.map(line => ({
        product_id: line.product_id,
        quantity: line.quantity,
        price_unit: line.price_unit
      })),
      invoice_date: date
    }]);

    res.json({
      success: true,
      invoice_id: invoiceId,
      status: 'created'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Record payment
app.post('/record-payment', async (req, res) => {
  try {
    const { invoice_id, amount, journal_id, date } = req.body;

    // Create payment record
    const paymentId = await odooClient.call_kw('account.payment', 'create', [{
      payment_type: 'inbound',
      partner_type: 'customer',
      partner_id: await odooClient.call_kw('account.move', 'read', [invoice_id, ['partner_id']])[0].partner_id[0],
      amount,
      date,
      journal_id,
      move_id: invoice_id
    }]);

    // Post the payment
    await odooClient.call_kw('account.payment', 'action_post', [paymentId]);

    res.json({
      success: true,
      payment_id: paymentId,
      status: 'recorded'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get financial summary
app.post('/financial-summary', async (req, res) => {
  try {
    const { period_start, period_end } = req.body;

    // Get account moves for the period
    const moves = await odooClient.call_kw('account.move', 'search_read', [
      [
        ['date', '>=', period_start],
        ['date', '<=', period_end],
        ['state', '=', 'posted']
      ],
      ['name', 'date', 'amount_total', 'move_type']
    ]);

    // Calculate totals
    const income = moves
      .filter(move => move.move_type === 'out_invoice')
      .reduce((sum, move) => sum + move.amount_total, 0);

    const expenses = moves
      .filter(move => move.move_type === 'in_invoice')
      .reduce((sum, move) => sum + move.amount_total, 0);

    res.json({
      success: true,
      period: { start: period_start, end: period_end },
      summary: {
        total_income: income,
        total_expenses: expenses,
        net_profit: income - expenses,
        transaction_count: moves.length
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Search partners/customers
app.post('/search-partners', async (req, res) => {
  try {
    const { query } = req.body;

    const domain = query ? [['name', 'ilike', query]] : [];
    const partners = await odooClient.call_kw('res.partner', 'search_read', [
      domain,
      ['id', 'name', 'email', 'phone', 'is_company']
    ]);

    res.json({
      success: true,
      partners
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

const PORT = process.env.PORT || 3003;
app.listen(PORT, () => {
  console.log(`Odoo MCP server running on port ${PORT}`);
});