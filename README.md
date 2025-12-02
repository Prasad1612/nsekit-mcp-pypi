# NseKit-MCP — NSE India Real-time & Historical Data Server

**NseKit-MCP** is a high-performance FastMCP (Model Context Protocol) server that exposes **100+ tools** for accessing live and historical data from the **National Stock Exchange of India (NSE)** using the powerful [NseKit](https://github.com/Prasad1612/NseKit) Python library.

Perfect for AI agents (Claude, Grok, GPT, etc.), trading bots, backtesters, and research platforms.

---

### Features

- 100+ ready-to-use tools
- Live & historical equity, F&O, indices, IPOs, corporate actions
- Full option chains with OI, Volume, IV, PCR, Max Pain
- EOD bhavcopy, delivery data, FII/DII, bulk/block deals
- Built-in **NSE-safe rate limiting** (~3 req/sec)
- Clean **JSON output** (Pandas → list of dicts)
- Works with Claude Desktop, Cursor, Cline, Windsurf, etc. via FastMCP

---

### Installation

Use this MCP server via uv (Python package installer)

```bash
pip install uv
```

Add the following configuration to your MCP server configuration file:

```
{
  "mcpServers": {
    "NseKit-MCP": {
      "command": "uvx",
      "args": ["nsekit-mcp@latest"]
    }
  }
}
```

### Popular Tools

| Tool | Description |
|------|------------|
| `market_status()` | Market open/close, Nifty, Gift Nifty, Mcap |
| `stock_quote("RELIANCE")` | Live price + 5-level depth + delivery |
| `option_chain("NIFTY", True)` | Full Nifty/BankNifty option chain + Max Pain |
| `bhavcopy_with_delivery("02-12-2025")` | Full day closing + delivery % |
| `fii_dii_activity("Nse")` | Latest FII/DII net buying/selling |
| `current_ipos()` | All live Mainboard + SME IPOs with subscription |
| `hit_52week_high()` | Stocks hitting 52-week high today |

All tools return clean JSON arrays.

---

### Tool Categories

NSE_Live • Pre_Market • Index_Live • Equity_Live  
FnO_Live • Corporate_Events • IPO • Historical  
Equity_EOD • FnO_EOD • Regulatory (SEBI)

---

### Safety & Compliance

- Thread-safe rate limiting (0.35s delay between NSE calls)  
- Respects NSE's fair usage policy  
- For research, personal trading, and AI agent use only  

---

### Credits

- Data powered by NseKit  
- Server powered by FastMCP  
- Made with ❤️ for the Indian Quant & Algo community
