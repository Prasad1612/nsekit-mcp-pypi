from mcp.server.fastmcp import FastMCP
from NseKit import NseKit, Moneycontrol
import pandas as pd
import time                      
from threading import Lock

# ================================================================
#                   RATE LIMIT CONTROL (NSE Safe)
# ================================================================

RATE_LIMIT_SECONDS = 0.35   # NSE safe: ~3 requests/sec
_last_call_time = 0
_lock = Lock()

def rate_limit():
    """Ensures minimum delay between NSE API calls."""
    global _last_call_time
    with _lock:
        now = time.time()
        elapsed = now - _last_call_time
        if elapsed < RATE_LIMIT_SECONDS:
            time.sleep(RATE_LIMIT_SECONDS - elapsed)
        _last_call_time = time.time()

# ================================================================
#                   MCP + NseKit Initialization
# ================================================================

mcp = FastMCP("NseKit-MCP", json_response=True)

get = NseKit.Nse()
mc = Moneycontrol.MC()

# ================================================================
#                   Helper: DF → JSON
# ================================================================

def df_to_json(data):
    if isinstance(data, pd.DataFrame):
        return data.to_dict(orient="records")
    return data

# =====================================================================
# MARKET STATUS & TRADING INFO
# =====================================================================


@mcp.tool()
def market_status(mode: str = "Market Status"):
    """
    TOOL: market_status
    DESCRIPTION:
        Get current market status, total mcap, live Nifty50, or Gift Nifty value.
    PARAMETERS:
        mode: str – "Market Status" | "Mcap" | "Nifty50" | "Gift Nifty"
    RETURNS:
        JSON with live market metrics
    CATEGORY:
        NSE_Live
    """
    rate_limit()
    return df_to_json(get.nse_market_status(mode))

@mcp.tool()
def is_market_open(segment: str = "Capital Market"):
    """
    TOOL: is_market_open
    DESCRIPTION:
        Check if Capital Market, F&O, Currency, Commodity or Debt segment is open.
    PARAMETERS:
        segment: str – "Capital Market" | "Currency" | "Commodity" | "Debt" | "currencyfuture"
    RETURNS:
        Boolean – True if open
    CATEGORY:
        NSE_Live
    """
    rate_limit()
    return get.nse_is_market_open(segment)

@mcp.tool()
def trading_holidays(list_only: bool = False):
    """
    TOOL: trading_holidays
    DESCRIPTION:
        Get all NSE trading holidays for current year.
    PARAMETERS:
        list_only: bool – Return only date list if True
    RETURNS:
        JSON list or full holiday details
    CATEGORY:
        NSE_Reference
    """
    rate_limit()
    return df_to_json(get.nse_trading_holidays(list_only=list_only))

@mcp.tool()
def clearing_holidays(list_only: bool = False):
    """
    TOOL: clearing_holidays
    DESCRIPTION:
        Get all NSE clearing/settlement holidays.
    PARAMETERS:
        list_only: bool – Return only dates if True
    RETURNS:
        JSON list or full details
    CATEGORY:
        NSE_Reference
    """
    rate_limit()
    return df_to_json(get.nse_clearing_holidays(list_only=list_only))

@mcp.tool()
def is_trading_holiday(date: str = None):
    """
    TOOL: is_trading_holiday
    DESCRIPTION:
        Check if today or given date is trading holiday.
    PARAMETERS:
        date: str – Optional "DD-MM-YYYY"
    RETURNS:
        Boolean
    CATEGORY:
        NSE_Reference
    """
    rate_limit()
    return get.is_nse_trading_holiday(date)

@mcp.tool()
def is_clearing_holiday(date: str = None):
    """
    TOOL: is_clearing_holiday
    DESCRIPTION:
        Check if today or given date is clearing holiday.
    PARAMETERS:
        date: str – Optional "DD-MM-YYYY"
    RETURNS:
        Boolean
    CATEGORY:
        NSE_Reference
    """
    rate_limit()
    return get.is_nse_clearing_holiday(date)


# =====================================================================
# LIVE MARKET & REFERENCE DATA
# =====================================================================

@mcp.tool()
def live_market_turnover():
    """
    TOOL: live_market_turnover
    DESCRIPTION:
        Real-time turnover across Equity, F&O, Currency, Commodity segments.
    RETURNS:
        JSON with segment-wise turnover
    CATEGORY:
        NSE_Live
    """
    rate_limit()
    return df_to_json(get.nse_live_market_turnover())

@mcp.tool()
def reference_rates():
    """
    TOOL: reference_rates
    DESCRIPTION:
        Official NSE USD, EUR, GBP, JPY reference rates.
    RETURNS:
        JSON currency rates
    CATEGORY:
        NSE_Live
    """
    rate_limit()
    return df_to_json(get.nse_reference_rates())

@mcp.tool()
def gift_nifty_live():
    """
    TOOL: gift_nifty_live
    DESCRIPTION:
        Current Gift Nifty futures price and USDINR rate.
    RETURNS:
        JSON with Gift Nifty & USDINR
    CATEGORY:
        NSE_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_gifty_nifty())

@mcp.tool()
def market_statistics():
    """
    TOOL: market_statistics
    DESCRIPTION:
        Live capital market stats: Count of Advances, Declines, Unchanged, 52W High, 52W Low, Upper Circuit, Lower Circuit, Market Cap ₹ Lac Crs,
                                   Market Cap Tn $, Registered Investors (Raw), Registered Investors (Cr),
    RETURNS:
        JSON summary
    CATEGORY:
        NSE_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_market_statistics())


# =====================================================================
# PRE-OPEN & INDEX LIVE
# =====================================================================

@mcp.tool()
def preopen_index_summary(index_name: str = "NIFTY 50"):
    """
    TOOL: preopen_index_summary
    DESCRIPTION:
        Pre-open advance/decline for Nifty 50, Bank, Emerge, F&O, Others.
    PARAMETERS:
        index_name: str – "NIFTY 50" | "Nifty Bank" | "Emerge" | "Securities in F&O" | "Others" | "All"
    RETURNS:
        JSON pre-open summary
    CATEGORY:
        Pre_Market
    """
    rate_limit()
    return df_to_json(get.pre_market_nifty_info(index_name))

@mcp.tool()
def preopen_all_adv_dec():
    """
    TOOL: preopen_all_adv_dec
    DESCRIPTION:
        Full NSE pre-open advance/decline across all segments.
    RETURNS:
        JSON summary
    CATEGORY:
        Pre_Market
    """
    rate_limit()
    return df_to_json(get.pre_market_all_nse_adv_dec_info())

@mcp.tool()
def preopen_stocks(category: str = "NIFTY 50"):
    """
    TOOL: preopen_stocks
    DESCRIPTION:
        All stocks in pre-open with final price, change %.
    PARAMETERS:
        category: str – "All" | "NIFTY 50" | "Nifty Bank" | "Emerge" | "Securities in F&O"
    RETURNS:
        JSON list of stocks
    CATEGORY:
        Pre_Market
    """
    rate_limit()
    return df_to_json(get.pre_market_info(category))

@mcp.tool()
def all_indices_live():
    """
    TOOL: all_indices_live
    DESCRIPTION:
        Live values(open, high, low, close(last),variation,percentChange,yearHigh,yearLow,pe,pb,dy,declines,advances,unchanged) of all 150+ NSE indices.
    RETURNS:
        JSON list
    CATEGORY:
        Index_Live
    """
    rate_limit()
    return df_to_json(get.index_live_all_indices_data())

@mcp.tool()
def index_constituents_live_stocks_data(index_name: str, list_only: bool = False):
    """
    TOOL: index_constituents_live_stocks_data
    DESCRIPTION:
        Get stocks in any NSE index with live or current data.
    PARAMETERS:
        index_name: str – e.g. "NIFTY 50", "NIFTY IT"
        list_only: bool – Return only symbols if True, otherwise full data
    RETURNS:
        JSON constituents
    CATEGORY:
        Index_Live
    """
    rate_limit()
    return df_to_json(get.index_live_indices_stocks_data(index_name, list_only=list_only))


# =====================================================================
# LISTS & MASTER DATA
# =====================================================================

@mcp.tool()
def nifty50_constituents(list_only: bool = False):
    """
    TOOL: nifty50_constituents
    DESCRIPTION:
        Latest Nifty 50 stocks with sector & weight.
    PARAMETERS:
        list_only: bool – Only symbols if True
    RETURNS:
        JSON
    CATEGORY:
        Index_Reference
    """
    rate_limit()
    return df_to_json(get.nse_6m_nifty_50(list_only=list_only))

@mcp.tool()
def nifty500_constituents(list_only: bool = False):
    """
    TOOL: nifty500_constituents
    DESCRIPTION:
        Full Nifty 500 stock list.
    PARAMETERS:
        list_only: bool – Only symbols if True
    RETURNS:
        JSON
    CATEGORY:
        Index_Reference
    """
    rate_limit()
    return df_to_json(get.nse_6m_nifty_500(list_only=list_only))

@mcp.tool()
def fno_list(mode: str = "stocks", list_only: bool = False):
    """
    TOOL: fno_list
    DESCRIPTION:
        All F&O eligible stocks or indices.
    PARAMETERS:
        entity_type: str – "stocks" or "index"
        list_only: bool – Only symbols if True
    RETURNS:
        JSON
    CATEGORY:
        FnO_Reference
    """
    rate_limit()
    return df_to_json(get.nse_eom_fno_full_list(mode, list_only=list_only))

@mcp.tool()
def equity_master(list_only: bool = False):
    """
    TOOL: equity_master
    DESCRIPTION:
        Complete list of all NSE listed equities.
    PARAMETERS:
        list_only: bool – Only symbols if True
    RETURNS:
        JSON
    CATEGORY:
        Equity_Reference
    """
    rate_limit()
    return df_to_json(get.nse_eod_equity_full_list(list_only=list_only))


# =====================================================================
# OPTION CHAIN & F&O LIVE
# =====================================================================

@mcp.tool()
def option_chain(symbol: str, expiry: str = None, compact: bool = False):
    """
    TOOL: option_chain
    DESCRIPTION:
        Full live option chain with OI, volume, IV, PCR, Max Pain.
    PARAMETERS:
        symbol: str – "RELIANCE", "NIFTY", "BANKNIFTY"
        expiry: str – Optional "DD-MMM-YYYY"
        compact: bool – Compact OI view
    RETURNS:
        Complete option chain JSON
    CATEGORY:
        FnO_Live
    EXAMPLES:
        (get.fno_live_option_chain("RELIANCE"))                              Option chain for a stock symbol
        (get.fno_live_option_chain("NIFTY"))                                 Option chain for an index
        (get.fno_live_option_chain("RELIANCE", expiry_date="28-Oct-2025"))    Option chain with specific expiry
        (get.fno_live_option_chain("RELIANCE", oi_mode="compact"))           Compact option chain data
    """
    rate_limit()
    mode = "compact" if compact else None
    return df_to_json(get.fno_live_option_chain(symbol, expiry_date=expiry, oi_mode=mode))

@mcp.tool()
def expiry_dates(symbol: str = "NIFTY", filter_type: str = None):
    """
    TOOL: expiry_dates
    DESCRIPTION:
        Get All expiry dates or find particularly current, weekly, monthly expiry dates.
    PARAMETERS:
        symbol: str – Stock or index
        filter_type: str – "Current" | "Next Week" | "Month" | "All" → ["28-10-2025", "04-11-2025", "25-11-2025"]
    RETURNS:
        List of expiry dates
    CATEGORY:
        FnO_Reference
    EXAMPLES:
        (get.fno_expiry_dates())                                 # Nifty All Expiry Date
        (get.fno_expiry_dates("TCS"))                            # TCS All Expiry Date

        (get.fno_expiry_dates("NIFTY", "Current"))               # Nifty Current Expiry Date only → "28-10-2025"
        (get.fno_expiry_dates("NIFTY", "Next Week"))             # Nifty Next Week Expiry Date only → "04-11-2025"
        (get.fno_expiry_dates("NIFTY", "Month"))                 # Nifty Month Expiry Date only → "25-11-2025"
        (get.fno_expiry_dates("NIFTY", "All"))                   # → ["28-10-2025", "04-11-2025", "25-11-2025"]

        (get.fno_expiry_dates("TCS", "Current"))                 # TCS Current Expiry Date only
        (get.fno_expiry_dates("TCS", "Month"))                   # TCS Next Month Expiry Date only
    """
    rate_limit()
    return df_to_json(get.fno_expiry_dates(symbol, filter_type))

@mcp.tool()
def most_active_options(contract_type: str = "Stock", option_type: str = "Call", sort_by: str = "Volume"):
    """
    TOOL: most_active_options
    DESCRIPTION:
        Most active Call/Put by volume or value.
    PARAMETERS:
        contract_type: str – "Stock" or "Index"
        option_type: str – "Call" or "Put"
        sort_by: str – "Volume" or "Value"
    RETURNS:
        JSON top contracts
    CATEGORY:
        FnO_Live
    """
    rate_limit()
    return df_to_json(get.fno_live_most_active(contract_type, option_type, sort_by))


# =====================================================================
# EQUITY LIVE DATA
# =====================================================================

@mcp.tool()
def stock_quote(symbol: str):
    """
    TOOL: stock_quote
    DESCRIPTION:
        Full live quote: price, change, volume, VWAP, delivery, 5-level market depth, Sector, Industry, BasicIndustry, totalBuyQuantity, totalSellQuantity, UpperCircuit, LowerCircuit.
    PARAMETERS:
        symbol: str – NSE symbol
    RETURNS:
        Complete quote + order book
    CATEGORY:
        Equity_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_equity_price_info(symbol))

@mcp.tool()
def most_active_equities(by: str = "value"):
    """
    TOOL: most_active_equities
    DESCRIPTION:
        Top stocks by traded value or volume.
    PARAMETERS:
        by: str – "value" or "volume"
    RETURNS:
        JSON list
    CATEGORY:
        Equity_Live
    """
    rate_limit()
    func = get.cm_live_most_active_equity_by_value if by == "value" else get.cm_live_most_active_equity_by_vol
    return df_to_json(func())

@mcp.tool()
def volume_spurts():
    """
    TOOL: volume_spurts
    DESCRIPTION:
        Stocks with sudden volume surge vs average.
    RETURNS:
        JSON list
    CATEGORY:
        Equity_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_volume_spurts())

@mcp.tool()
def hit_52week_high():
    """
    TOOL: hit_52week_high
    DESCRIPTION:
        live market stocks hitting 52-week high today.
    RETURNS:
        JSON list
    CATEGORY:
        Equity_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_52week_high())

@mcp.tool()
def hit_52week_low():
    """
    TOOL: hit_52week_low
    DESCRIPTION:
        live market stocks hitting 52-week low today.
    RETURNS:
        JSON list
    CATEGORY:
        Equity_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_52week_low())


# =====================================================================
# CORPORATE ACTIONS & EVENTS
# =====================================================================

@mcp.tool()
def insider_trading(symbol: str = None, period: str = None, start_date: str = None, end_date: str = None):
    """
    TOOL: insider_trading
    DESCRIPTION:
        Latest insider buying/selling (SAST).
    PARAMETERS:
        symbol: str – Optional
        period: str – "1D"|"1W"|"1M"|"3M"|"6M"|"1Y"
        start_date, end_date: str – "DD-MM-YYYY"
    RETURNS:
        JSON transactions
    CATEGORY:
        Corporate_Events
    """
    rate_limit()
    return df_to_json(get.cm_live_hist_insider_trading(symbol, period, start_date, end_date))

@mcp.tool()
def corporate_actions(symbol: str = None, period: str = None, start_date: str = None, end_date: str = None, purpose: str = None):
    """
    TOOL: corporate_actions
    DESCRIPTION:
        Dividends, bonus, splits, rights, buyback.
    PARAMETERS:
        symbol, purpose: str – Optional filter
        period: str – "1M"|"3M"|"6M"|"1Y"
    RETURNS:
        JSON list
    CATEGORY:
        Corporate_Events
    """
    rate_limit()
    return df_to_json(get.cm_live_hist_corporate_action(symbol, period, start_date, end_date, purpose))

@mcp.tool()
def board_meetings(symbol: str = None, start_date: str = None, end_date: str = None):
    """
    TOOL: board_meetings
    DESCRIPTION:
        Upcoming & past board meetings.
    RETURNS:
        JSON list
    CATEGORY:
        Corporate_Events
    """
    rate_limit()
    return df_to_json(get.cm_live_hist_board_meetings(symbol, start_date, end_date))


# =====================================================================
# IPO & LISTINGS
# =====================================================================

@mcp.tool()
def current_ipos():
    """
    TOOL: current_ipos
    DESCRIPTION:
        All open Mainboard & SME IPOs with subscription status.
    RETURNS:
        JSON dashboard
    CATEGORY:
        IPO
    """
    rate_limit()
    return df_to_json(get.ipo_current())

@mcp.tool()
def ipo_preopen_today():
    """
    TOOL: ipo_preopen_today
    DESCRIPTION:
        Newly listed IPOs in special pre-open session.
    RETURNS:
        JSON list
    CATEGORY:
        IPO
    """
    rate_limit()
    return df_to_json(get.ipo_preopen())

@mcp.tool()
def ipo_tracker(board: str = "Mainboard"):
    """
    TOOL: ipo_tracker
    DESCRIPTION:
        YTD IPO listing performance & gains.
    PARAMETERS:
        board: str – "Mainboard" | "SME" | None
    RETURNS:
        JSON tracker
    CATEGORY:
        IPO
    """
    rate_limit()
    return df_to_json(get.ipo_tracker_summary(board))


# =====================================================================
# HISTORICAL & EOD DATA
# =====================================================================

@mcp.tool()
def index_history(index: str, period: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: index_history
    DESCRIPTION:
        Fetch historical OHLC + turnover for any index.
    PARAMETERS:
        index: str – "NIFTY 50", "NIFTY BANK", etc. –Name of the index
        period: str – Shortcut period ("1D","1W","1M","3M","6M","1Y","2Y","5Y","10Y","YTD","MAX")
        from_date: str – Start date in DD-MM-YYYY (optional)
        to_date: str – End date in DD-MM-YYYY (optional)
    RETURNS:
        JSON with daily OHLC + turnover
    CATEGORY:
        Historical
    EXAMPLES:
        index_history("NIFTY 50", period="1Y")
        index_history("NIFTY 50", from_date="01-01-2025")
        index_history("NIFTY BANK", from_date="01-01-2025", to_date="17-10-2025")
    """
    
    rate_limit()
    return df_to_json(get.index_historical_data(index=index, period=period, from_date=from_date, to_date=to_date))


@mcp.tool()
def stock_history(symbol: str, period: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: stock_history
    DESCRIPTION:
        Fetch historical price OHLC + turnover + delivery data for any stock.
    PARAMETERS:
        index: str – "TCS", "ITC", etc. –Name of the stock
        period: str – Shortcut period ("1D","1W","1M","3M","6M","1Y","2Y","5Y","10Y","YTD","MAX")
        from_date: str – Start date in DD-MM-YYYY (optional)
        to_date: str – End date in DD-MM-YYYY (optional)
    RETURNS:
        JSON with daily OHLCV + turnover + delivery
    CATEGORY:
        Historical
    EXAMPLES:
        stock_history("TCS", period="1Y")
        stock_history("TCS", from_date="01-01-2025")
        stock_history("TCS", from_date="01-01-2025", to_date="17-10-2025")
    """

    rate_limit()
    return df_to_json(get.cm_hist_security_wise_data(symbol=symbol, period=period, from_date=from_date, to_date=to_date))


# =====================================================================
#                          NSE Data - Historical
# =====================================================================

@mcp.tool()
def nse_live_hist_circulars(from_date: str = None, to_date: str = None, department: str = None):
    """
    TOOL: nse_live_hist_circulars
    DESCRIPTION:
        Historical NSE circulars (default: yesterday → today)
    PARAMETERS:
        from_date: str – "DD-MM-YYYY" (optional)
        to_date: str – "DD-MM-YYYY" (optional)
        department: str – e.g., "NSE Listing" (optional filter)
    RETURNS:
        List of circulars
    CATEGORY:
        NSE_Historical
    """
    rate_limit()
    # Original: get.nse_live_hist_circulars(from_date, to_date) or with department
    return df_to_json(get.nse_live_hist_circulars(from_date, to_date, department))


@mcp.tool()
def nse_live_hist_press_releases(from_date: str = None, to_date: str = None, department: str = None):
    """
    TOOL: nse_live_hist_press_releases
    DESCRIPTION:
        Historical NSE press releases
    PARAMETERS:
        from_date: str – "DD-MM-YYYY"
        to_date: str – "DD-MM-YYYY"
        department: str – e.g., Corporate Communications , Investor Services Cell , Member Compliance , NSE Clearing , NSE Indices , NSE Listing , Surveillance 
    RETURNS:
        List of press releases
    CATEGORY:
        NSE_Historical
    """
    rate_limit()
    # Original: get.nse_live_hist_press_releases(...)
    return df_to_json(get.nse_live_hist_press_releases(from_date, to_date, department))


# =====================================================================
#                          Index Live Data
# =====================================================================

@mcp.tool()
def index_live_nifty_50_returns():
    """
    TOOL: index_live_nifty_50_returns
    DESCRIPTION:
        Nifty 50 returns summary (1W to 5Y)
    PARAMETERS: None
    RETURNS:
        Returns % across timeframes
    CATEGORY:
        Index_Live
    """
    rate_limit()
    # Original: get.index_live_nifty_50_returns()
    return df_to_json(get.index_live_nifty_50_returns())


@mcp.tool()
def index_live_nifty_50_contribution():
    """
    TOOL: index_live_nifty_50_contribution
    DESCRIPTION:
        Stock-wise contribution to Nifty 50 index movement
    PARAMETERS: None
    RETURNS:
        Contribution data
    CATEGORY:
        Index_Live
    """
    rate_limit()
    # Original: get.index_live_nifty_50_contribution()
    return df_to_json(get.index_live_nifty_50_contribution())


# =====================================================================
#                          Index EOD & Historical
# =====================================================================

@mcp.tool()
def index_eod_bhav_copy(date: str):
    """
    TOOL: index_eod_bhav_copy
    DESCRIPTION:
        All indices EOD bhavcopy for a specific date
    PARAMETERS:
        date: str – "DD-MM-YYYY"
    RETURNS:
        Full index bhavcopy DataFrame
    CATEGORY:
        Index_EOD
    """
    rate_limit()
    # Original: get.index_eod_bhav_copy("17-10-2025")
    return df_to_json(get.index_eod_bhav_copy(date))


@mcp.tool()
def index_pe_pb_div_historical_data(index: str, period: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: index_pe_pb_div_historical_data
    DESCRIPTION:
        Historical P/E, P/B, Dividend Yield for any index
    PARAMETERS:
        index: str – "NIFTY 50", "NIFTY BANK" etc.
        period: str – Shortcut period ("1D","1W","1M","3M","6M","1Y","2Y","5Y","10Y","YTD","MAX")
        from_date: str – Start date in DD-MM-YYYY (optional)
        to_date: str – End date in DD-MM-YYYY (optional)
    RETURNS:
        Historical valuation data
    CATEGORY:
        Index_Historical
    """
    rate_limit()
    return df_to_json(get.index_pe_pb_div_historical_data(index=index, period=period, from_date=from_date, to_date=to_date))


@mcp.tool()
def india_vix_historical_data(period: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: india_vix_historical_data
    DESCRIPTION:
        Historical India VIX data
    PARAMETERS:
        period: str – Shortcut period ("1D","1W","1M","3M","6M","1Y","2Y","5Y","10Y","YTD","MAX")
        from_date: str – Start date in DD-MM-YYYY (optional)
        to_date: str – End date in DD-MM-YYYY (optional)
    RETURNS:
        India VIX time series
    CATEGORY:
        India_VIX_Historical
    """
    rate_limit()
    return df_to_json(get.india_vix_historical_data(period=period, from_date=from_date, to_date=to_date))


# =====================================================================
#                       Capital Market Live Data
# =====================================================================

@mcp.tool()
def cm_live_equity_info(symbol: str):
    """
    TOOL: cm_live_equity_info
    DESCRIPTION:
        Live equity master info (face value, ISIN, sector etc.)
    PARAMETERS:
        symbol: str – e.g., "RELIANCE"
    RETURNS:
        Equity details
    CATEGORY:
        CM_Live
    """
    rate_limit()
    # Original: get.cm_live_equity_info("RELIANCE")
    return (get.cm_live_equity_info(symbol))


@mcp.tool()
def cm_live_block_deal():
    """
    TOOL: cm_live_block_deal
    DESCRIPTION:
        Latest block deals (live)
    PARAMETERS: None
    RETURNS:
        Block deal data
    CATEGORY:
        CM_Live
    """
    rate_limit()
    # Original: get.cm_live_block_deal()
    return df_to_json(get.cm_live_block_deal())


@mcp.tool()
def cm_live_hist_corporate_announcement(symbol: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: cm_live_hist_corporate_announcement
    DESCRIPTION:
        Corporate announcements (all or symbol-specific)
    PARAMETERS:
        symbol: str – optional, e.g., "RELIANCE"
        from_date: str – "DD-MM-YYYY"
        to_date: str – "DD-MM-YYYY"
    RETURNS:
        Announcement list
    CATEGORY:
        CM_Live
    """
    rate_limit()
    # Original: get.cm_live_hist_corporate_announcement("RELIANCE", "01-01-2025", "15-10-2025")
    return df_to_json(get.cm_live_hist_corporate_announcement(symbol, from_date, to_date))


@mcp.tool()
def cm_live_today_event_calendar(date_from: str = None, date_to: str = None):
    """
    TOOL: cm_live_today_event_calendar
    DESCRIPTION:
        Today's or date-range corporate events (AGM, results etc.)
    PARAMETERS:
        date_from: str – optional
        date_to: str – optional
    RETURNS:
        Event calendar
    CATEGORY:
        CM_Live
    """
    rate_limit()
    # Original: get.cm_live_today_event_calendar("01-01-2025", "01-01-2025")
    return df_to_json(get.cm_live_today_event_calendar(date_from, date_to))


@mcp.tool()
def cm_live_upcoming_event_calendar():
    """
    TOOL: cm_live_upcoming_event_calendar
    DESCRIPTION:
        Upcoming corporate events
    PARAMETERS: None
    RETURNS:
        Upcoming events
    CATEGORY:
        CM_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_upcoming_event_calendar())


@mcp.tool()
def cm_live_hist_shareholder_meetings(symbol: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: cm_live_hist_shareholder_meetings
    DESCRIPTION:
        Shareholder meetings (AGM/EGM) history
    PARAMETERS:
        symbol: str – optional
        from_date: str – optional
        to_date: str – optional
    RETURNS:
        Meeting data
    CATEGORY:
        CM_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_hist_Shareholder_meetings(symbol, from_date, to_date))


@mcp.tool()
def cm_live_hist_qualified_institutional_placement(stage: str = None, period_or_symbol: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: cm_live_hist_qualified_institutional_placement
    DESCRIPTION:
        QIP data by stage, period, symbol
    PARAMETERS:
        stage: str – "In-Principle" or "Listing Stage"
        period_or_symbol: str – "1Y", "RELIANCE" etc.
        from_date: str – optional
        to_date: str – optional
    RETURNS:
        QIP records
    CATEGORY:
        CM_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_hist_qualified_institutional_placement(stage, period_or_symbol, from_date, to_date))


@mcp.tool()
def cm_live_hist_preferential_issue(stage: str = None, period_or_symbol: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: cm_live_hist_preferential_issue
    DESCRIPTION:
        Preferential issue data
    PARAMETERS:
        stage: str – "In-Principle" or "Listing Stage"
        period_or_symbol: str – "1Y", "RELIANCE" etc.
        from_date: str – optional
        to_date: str – optional
    RETURNS:
        Preferential issues
    CATEGORY:
        CM_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_hist_preferential_issue(stage, period_or_symbol, from_date, to_date))


@mcp.tool()
def cm_live_hist_right_issue(stage: str = None, period_or_symbol: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: cm_live_hist_right_issue
    DESCRIPTION:
        Rights issue data
    PARAMETERS:
        stage: str – "In-Principle" or "Listing Stage"
        period_or_symbol: str – "1Y", "RELIANCE" etc.
        from_date: str – optional
        to_date: str – optional
    RETURNS:
        Rights issues
    CATEGORY:
        CM_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_hist_right_issue(stage, period_or_symbol, from_date, to_date))


@mcp.tool()
def cm_live_voting_results():
    """
    TOOL: cm_live_voting_results
    DESCRIPTION:
        Latest voting results
    PARAMETERS: None
    RETURNS:
        Voting outcomes
    CATEGORY:
        CM_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_voting_results())


@mcp.tool()
def cm_live_qtly_shareholding_patterns():
    """
    TOOL: cm_live_qtly_shareholding_patterns
    DESCRIPTION:
        Latest quarterly shareholding patterns
    PARAMETERS: None
    RETURNS:
        SHP data
    CATEGORY:
        CM_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_qtly_shareholding_patterns())


@mcp.tool()
def cm_live_hist_annual_reports(symbol: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: cm_live_hist_annual_reports
    DESCRIPTION:
        Annual reports (all or symbol-specific)
    PARAMETERS:
        symbol: str – optional
        from_date/to_date: str – optional
    RETURNS:
        Annual report links/data
    CATEGORY:
        CM_Live
    """
    rate_limit()
    return df_to_json(get.cm_live_hist_annual_reports(symbol, from_date, to_date))

# =====================================================================
#                          FnO Live Data
# =====================================================================

@mcp.tool()
def fno_live_futures_data(symbol: str):
    """
    TOOL: fno_live_futures_data
    DESCRIPTION:
        Live futures data for stock or index
    PARAMETERS:
        symbol: str – "RELIANCE" or "NIFTY"
    RETURNS:
        Futures snapshot
    CATEGORY:
        FnO_Live
    """
    rate_limit()
    return df_to_json(get.fno_live_futures_data(symbol))


@mcp.tool()
def fno_live_most_active_futures_contracts(by: str = "Volume"):
    """
    TOOL: fno_live_most_active_futures_contracts
    DESCRIPTION:
        Most active futures by Volume or Value
    PARAMETERS:
        by: str – "Volume" or "Value"
    RETURNS:
        Top futures contracts
    CATEGORY:
        FnO_Live
    """
    rate_limit()
    return df_to_json(get.fno_live_most_active_futures_contracts(by))


@mcp.tool()
def fno_live_most_active_contracts_by_oi():
    """
    TOOL: fno_live_most_active_contracts_by_oi
    DESCRIPTION:
        Most active contracts by Open Interest
    PARAMETERS: None
    RETURNS:
        Top OI contracts
    CATEGORY:
        FnO_Live
    """
    rate_limit()
    return df_to_json(get.fno_live_most_active_contracts_by_oi())


@mcp.tool()
def fno_live_most_active_contracts_by_volume():
    """
    TOOL: fno_live_most_active_contracts_by_volume
    DESCRIPTION:
        Most active by volume
    PARAMETERS: None
    RETURNS:
        Volume leaders
    CATEGORY:
        FnO_Live
    """
    rate_limit()
    return df_to_json(get.fno_live_most_active_contracts_by_volume())


@mcp.tool()
def fno_live_most_active_options_contracts_by_volume():
    """
    TOOL: fno_live_most_active_options_contracts_by_volume
    DESCRIPTION:
        Top options contracts by volume
    PARAMETERS: None
    RETURNS:
        Active options
    CATEGORY:
        FnO_Live
    """
    rate_limit()
    return df_to_json(get.fno_live_most_active_options_contracts_by_volume())


@mcp.tool()
def fno_live_most_active_underlying():
    """
    TOOL: fno_live_most_active_underlying
    DESCRIPTION:
        Most active underlying stocks/indices
    PARAMETERS: None
    RETURNS:
        Underlying activity
    CATEGORY:
        FnO_Live
    """
    rate_limit()
    return df_to_json(get.fno_live_most_active_underlying())


@mcp.tool()
def fno_live_change_in_oi():
    """
    TOOL: fno_live_change_in_oi
    DESCRIPTION:
        Change in Open Interest across contracts
    PARAMETERS: None
    RETURNS:
        OI change data
    CATEGORY:
        FnO_Live
    """
    rate_limit()
    return df_to_json(get.fno_live_change_in_oi())


@mcp.tool()
def fno_live_active_contracts(symbol: str = "NIFTY", expiry_date: str = None):
    """
    TOOL: fno_live_active_contracts
    DESCRIPTION:
        Active NIFTY/BANKNIFTY & stock option contracts
    PARAMETERS:
        symbol: str – "NIFTY", "BANKNIFTY" , RELIANCE , TCS, etc
        expiry_date: str – optional "DD-MM-YYYY"
    RETURNS:
        Active index or stock options contracts
    CATEGORY:
        FnO_Live
    """
    rate_limit()
    return df_to_json(get.fno_live_active_contracts(symbol, expiry_date=expiry_date))


# =====================================================================
#                         EQUITY EOD DATA
# =====================================================================

@mcp.tool()
def fii_dii_activity(exchange: str = None):
    """
    TOOL: fii_dii_activity
    DESCRIPTION:
        Latest FII/DII net buying/selling activity.
    PARAMETERS:
        exchange: str – "Nse" NSE only FII/DII net buying/selling activity.
    RETURNS:
        FII/DII cash segment activity
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_fii_dii_activity()
    # Original: get.cm_eod_fii_dii_activity("Nse") 
    return df_to_json(get.cm_eod_fii_dii_activity(exchange))


@mcp.tool()
def market_activity_report(date: str):
    """
    TOOL: market_activity_report
    DESCRIPTION:
        Daily market turnover, advances/declines, top gainers/losers.
    PARAMETERS:
        date: str – Trade date in "DD-MM-YYYY"
    RETURNS:
        Full market activity report
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_market_activity_report("17-10-2025")
    return df_to_json(get.cm_eod_market_activity_report(date))

# @mcp.tool()
# def market_activity_report(date: str):
#     """
#     TOOL: market_activity_report
#     DESCRIPTION:
#         Daily market turnover, advances/declines, top gainers/losers.
#     PARAMETERS:
#         date: str – Trade date in "DD-MM-YYYY"
#     RETURNS:
#         Full market activity report
#     CATEGORY:
#         Equity_EOD
#     """
#     rate_limit()

#     date_obj = datetime.strptime(date, "%d-%m-%Y").date()

#     data = get.cm_eod_market_activity_report(date_obj)

#     return (data)


@mcp.tool()
def bhavcopy_with_delivery(date: str):
    """
    TOOL: bhavcopy_with_delivery
    DESCRIPTION:
        Full NSE equity bhavcopy including delivery percentage & value.
    PARAMETERS:
        date: str – "DD-MM-YYYY"
    RETURNS:
        Complete bhavcopy with delivery data
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_bhavcopy_with_delivery("17-10-2025")
    return df_to_json(get.cm_eod_bhavcopy_with_delivery(date))


@mcp.tool()
def equity_bhavcopy(date: str):
    """
    TOOL: equity_bhavcopy
    DESCRIPTION:
        Standard equity closing prices, volume, trades (without delivery).
    PARAMETERS:
        date: str – "DD-MM-YYYY"
    RETURNS:
        Equity-only bhavcopy
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_equity_bhavcopy("17-10-2025")
    return df_to_json(get.cm_eod_equity_bhavcopy(date))


@mcp.tool()
def week_52_high_low(date: str):
    """
    TOOL: week_52_high_low
    DESCRIPTION:
        Stocks hitting 52-week high or low on given date.
    PARAMETERS:
        date: str – "DD-MM-YYYY"
    RETURNS:
        List of 52-week high/low stocks
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_52_week_high_low("17-10-2025")
    return df_to_json(get.cm_eod_52_week_high_low(date))


@mcp.tool()
def bulk_deals_EOD():
    """
    TOOL: bulk_deals_EOD
    DESCRIPTION:
        End of day based bulk deals across NSE/BSE (client-level).
    PARAMETERS: None
    RETURNS:
        Today's bulk deals
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_bulk_deal()
    return df_to_json(get.cm_eod_bulk_deal())


@mcp.tool()
def block_deals_EOD():
    """
    TOOL: block_deals_EOD
    DESCRIPTION:
        End of day based block deals (large negotiated trades).
    PARAMETERS: None
    RETURNS:
        Today's block deals
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_block_deal()
    return df_to_json(get.cm_eod_block_deal())


@mcp.tool()
def short_selling(date: str):
    """
    TOOL: short_selling
    DESCRIPTION:
        Stocks disclosed for short selling on a given date if user no date given last trading date is used.
    PARAMETERS:
        date: str – "DD-MM-YYYY"
    RETURNS:
        Short delivery positions
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_shortselling("17-10-2025")
    return df_to_json(get.cm_eod_shortselling(date))


@mcp.tool()
def surveillance_indicator(date: str):
    """
    TOOL: surveillance_indicator
    DESCRIPTION:
        Stocks under ASM/GSM/Z-category surveillance.
    PARAMETERS:
        date: str – "DD-MM-YY" (2-digit year) if user no date given last trading date is used.
    RETURNS:
        Surveillance list
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_surveillance_indicator("17-10-25")
    return df_to_json(get.cm_eod_surveillance_indicator(date))


@mcp.tool()
def series_change_latest():
    """
    TOOL: series_change_latest
    DESCRIPTION:
        Recent changes in trading series (EQ → BE, BE → BZ etc.).
    PARAMETERS: None
    RETURNS:
        Latest series changes
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_series_change()
    return df_to_json(get.cm_eod_series_change())


@mcp.tool()
def equity_band_changes(date: str):
    """
    TOOL: equity_band_changes
    DESCRIPTION:
        Stocks moved to/from price bands (2%, 5%, 10%, 20%).
    PARAMETERS:
        date: str – "DD-MM-YYYY"    if user no date given last trading date is used.
    RETURNS:
        Price band changes
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_eq_band_changes("17-10-2025")
    return df_to_json(get.cm_eod_eq_band_changes(date))


@mcp.tool()
def equity_price_bands_eod(date: str):
    """
    TOOL: equity_price_bands_eod
    DESCRIPTION:
        Applicable price bands for all stocks on a given EOD.
    PARAMETERS:
        date: str – "DD-MM-YYYY"    if user no date given last trading date is used.
    RETURNS:
        Full price band data
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_eq_price_band("17-10-2025")
    return df_to_json(get.cm_eod_eq_price_band(date))


@mcp.tool()
def equity_price_bands_historical(symbol: str = None, period: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: equity_price_bands_historical
    DESCRIPTION:
        Historical price band changes for a stock or all stocks.
    PARAMETERS:
        symbol: str – Optional stock symbol
        period: str – "1D", "1W", "1M", "3M", "6M", "1Y"
        from_date: str – "DD-MM-YYYY"   (optional)
        to_date: str – "DD-MM-YYYY"   (optional)
    RETURNS:
        Price band history
    CATEGORY:
        Equity_Historical
    """
    rate_limit()
    # Original examples:
    # get.cm_hist_eq_price_band()
    # get.cm_hist_eq_price_band("1W")
    # get.cm_hist_eq_price_band("01-10-2025")
    # get.cm_hist_eq_price_band("15-10-2025", "17-10-2025")
    # get.cm_hist_eq_price_band("WEWIN")
    return df_to_json(get.cm_hist_eq_price_band(symbol=symbol, period=period, from_date=from_date, to_date=to_date))


@mcp.tool()
def pe_ratio(date: str):
    """
    TOOL: pe_ratio
    DESCRIPTION:
        PE, PB, Dividend Yield for all listed companies.
    PARAMETERS:
        date: str – "DD-MM-YY"  if user no date given last trading date is used.
    RETURNS:
        Valuation ratios
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_pe_ratio("17-10-25")
    return df_to_json(get.cm_eod_pe_ratio(date))


@mcp.tool()
def market_cap(date: str):
    """
    TOOL: market_cap
    DESCRIPTION:
        Market capitalization of all companies.
    PARAMETERS:
        date: str – "DD-MM-YY"  if user no date given last trading date is used.
    RETURNS:
        Market cap data
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_mcap("17-10-25")
    return df_to_json(get.cm_eod_mcap(date))


@mcp.tool()
def equity_name_change_latest():
    """
    TOOL: equity_name_change_latest
    DESCRIPTION:
        Recent corporate name changes.
    PARAMETERS: None
    RETURNS:
        Name change announcements
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_eq_name_change()
    return df_to_json(get.cm_eod_eq_name_change())


@mcp.tool()
def equity_symbol_change_latest():
    """
    TOOL: equity_symbol_change_latest
    DESCRIPTION:
        Recent symbol changes (e.g., INFY → INFY).
    PARAMETERS: None
    RETURNS:
        Symbol change list
    CATEGORY:
        Equity_EOD
    """
    rate_limit()
    # Original: get.cm_eod_eq_symbol_change()
    return df_to_json(get.cm_eod_eq_symbol_change())


@mcp.tool()
def historical_bulk_deals(symbol: str = None, period: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: historical_bulk_deals
    DESCRIPTION:
        Bulk deals history – by symbol, date range or period.
    PARAMETERS:
        symbol: str – Optional
        period: str – "1D", "1W", "1M", "3M", "6M", "1Y".
        from_date/to_date: str – "DD-MM-YYYY"   Optional
    RETURNS:
        Bulk deals history
    CATEGORY:
        Equity_Historical
    """
    rate_limit()
    # Original: get.cm_hist_bulk_deals(...) variants
    return df_to_json(get.cm_hist_bulk_deals(symbol=symbol, period=period, from_date=from_date, to_date=to_date))


@mcp.tool()
def historical_block_deals(symbol: str = None, period: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: historical_block_deals
    DESCRIPTION:
        Block deals history – by symbol or date range.
    PARAMETERS:
        symbol: str – Optional
        period: str – "1D", "1W", "1M", "3M", "6M", "1Y".
        from_date/to_date: str – "DD-MM-YYYY"   Optional
    RETURNS:
        Block deals history
    CATEGORY:
        Equity_Historical
    """
    rate_limit()
    return df_to_json(get.cm_hist_block_deals(symbol=symbol, period=period, from_date=from_date, to_date=to_date))


@mcp.tool()
def historical_short_selling(symbol: str = None, period: str = None, from_date: str = None, to_date: str = None):
    """
    TOOL: historical_short_selling
    DESCRIPTION:
        Historical short selling disclosures.
    PARAMETERS:
        symbol: str – Optional
        period: str – "1D", "1W", "1M", "3M", "6M", "1Y".
        from_date/to_date: str – "DD-MM-YYYY"   Optional
    RETURNS:
        Short selling data
    CATEGORY:
        Equity_Historical
    """
    rate_limit()
    return df_to_json(get.cm_hist_short_selling(symbol, period or from_date, to_date))


@mcp.tool()
def business_growth(mode: str = "daily", month: str = None, year: int = None):
    """
    TOOL: business_growth
    DESCRIPTION:
        NSE daily/monthly/yearly business growth (cash segment).
    PARAMETERS:
        mode: str – "daily", "monthly", "yearly"
        month: str – "OCT", "JAN" etc. (for daily)
        year: int – FY year
    RETURNS:
        Business turnover growth
    CATEGORY:
        Market_Stats
    """
    rate_limit()
    # Original: get.cm_dmy_biz_growth(...)
    return df_to_json(get.cm_dmy_biz_growth(mode, month, year))


@mcp.tool()
def monthly_settlement_report(period: str = None, start_year: int = None, end_year: int = None):
    """
    TOOL: monthly_settlement_report
    DESCRIPTION:
        Monthly settlement statistics (cash segment).
    PARAMETERS:
        period: str – "1Y", "3Y" or None (current FY)
        start_year/end_year: int – e.g., 2024, 2026
    RETURNS:
        Settlement stats
    CATEGORY:
        Market_Stats
    """
    rate_limit()
    # Original: get.cm_monthly_settlement_report(...)
    return df_to_json(get.cm_monthly_settlement_report(period or start_year, end_year))


@mcp.tool()
def monthly_most_active_equity():
    """
    TOOL: monthly_most_active_equity
    DESCRIPTION:
        Most active stocks by volume/value in latest month.
    PARAMETERS: None
    RETURNS:
        Top active equities
    CATEGORY:
        Market_Stats
    """
    rate_limit()
    # Original: get.cm_monthly_most_active_equity()
    return df_to_json(get.cm_monthly_most_active_equity())


@mcp.tool()
def advances_declines(mode: str = "Month_wise", month: str = None, year: int = None):
    """
    TOOL: advances_declines
    DESCRIPTION:
        Historical advances vs declines (daily or monthly).
    PARAMETERS:
        mode: str – "Day_wise" or "Month_wise"
        month: str – "SEP", "OCT" etc.
        year: int – e.g., 2025
    RETURNS:
        A/D data
    CATEGORY:
        Market_Stats
    """
    rate_limit()
    # Original: get.historical_advances_decline(...)
    return df_to_json(get.historical_advances_decline(mode, month, year))


# =====================================================================
#                         F&O EOD & HISTORICAL DATA
# =====================================================================

@mcp.tool()
def fno_bhavcopy(date: str):
    """
    TOOL: fno_bhavcopy
    DESCRIPTION:
        Full F&O bhavcopy (futures + options).
    PARAMETERS:
        date: str – "DD-MM-YYYY"    if user no date given last trading date is used.
    RETURNS:
        Complete F&O closing data
    CATEGORY:
        FnO_EOD
    """
    rate_limit()
    # Original: get.fno_eod_bhav_copy("17-10-2025")
    return df_to_json(get.fno_eod_bhav_copy(date))


@mcp.tool()
def fii_stats_fno(date: str):
    """
    TOOL: fii_stats_fno
    DESCRIPTION:
        FII activity in F&O segment (Index/Stock, Long/Short).
    PARAMETERS:
        date: str – "DD-MM-YYYY"    if user no date given last trading date is used.
    RETURNS:
        FII F&O stats
    CATEGORY:
        FnO_EOD
    """
    rate_limit()
    # Original: get.fno_eod_fii_stats("17-10-2025")
    return df_to_json(get.fno_eod_fii_stats(date))


@mcp.tool()
def top10_futures(date: str):
    """
    TOOL: top10_futures
    DESCRIPTION:
        Top 10 most active futures contracts by volume/OI.
    PARAMETERS:
        date: str – "DD-MM-YYYY"    if user no date given last trading date is used.
    RETURNS:
        Top 10 futures
    CATEGORY:
        FnO_EOD
    """
    rate_limit()
    # Original: get.fno_eod_top10_fut("17-10-2025")
    return (get.fno_eod_top10_fut(date))


@mcp.tool()
def top20_options(date: str):
    """
    TOOL: top20_options
    DESCRIPTION:
        Top 20 most active options contracts.
    PARAMETERS:
        date: str – "DD-MM-YYYY"    if user no date given last trading date is used.
    RETURNS:
        Top 20 options
    CATEGORY:
        FnO_EOD
    """
    rate_limit()
    # Original: get.fno_eod_top20_opt("17-10-2025")
    return (get.fno_eod_top20_opt(date))


@mcp.tool()
def security_ban_list(date: str):
    """
    TOOL: security_ban_list
    DESCRIPTION:
        Stocks under F&O ban period.
    PARAMETERS:
        date: str – "DD-MM-YYYY"    if user no date given last trading date is used.
    RETURNS:
        Ban list
    CATEGORY:
        FnO_EOD
    """
    rate_limit()
    # Original: get.fno_eod_sec_ban("17-10-2025")
    return df_to_json(get.fno_eod_sec_ban(date))


@mcp.tool()
def mwpl_data(date: str):
    """
    TOOL: mwpl_data
    DESCRIPTION:
        Market Wide Position Limits (MWPL) and usage %.
    PARAMETERS:
        date: str – "DD-MM-YYYY"    if user no date given last trading date is used.
    RETURNS:
        MWPL report
    CATEGORY:
        FnO_EOD
    """
    rate_limit()
    # Original: get.fno_eod_mwpl_3("17-10-2025")
    return df_to_json(get.fno_eod_mwpl_3(date))


@mcp.tool()
def combined_oi(date: str):
    """
    TOOL: combined_oi
    DESCRIPTION:
        Combined futures & options open interest.
    PARAMETERS:
        date: str – "DD-MM-YYYY"    if user no date given last trading date is used.
    RETURNS:
        OI snapshot
    CATEGORY:
        FnO_EOD
    """
    rate_limit()
    # Original: get.fno_eod_combine_oi("17-10-2025")
    return df_to_json(get.fno_eod_combine_oi(date))


@mcp.tool()
def participant_oi(date: str):
    """
    TOOL: participant_oi
    DESCRIPTION:
        FII, DII, Pro, Client wise open interest.
    PARAMETERS:
        date: str – "DD-MM-YYYY"    if user no date given last trading date is used.
    RETURNS:
        Participant OI
    CATEGORY:
        FnO_EOD
    """
    rate_limit()
    # Original: get.fno_eod_participant_wise_oi("17-10-2025")
    return df_to_json(get.fno_eod_participant_wise_oi(date))


@mcp.tool()
def participant_volume(date: str):
    """
    TOOL: participant_volume
    DESCRIPTION:
        Participant-wise trading volume in F&O.
    PARAMETERS:
        date: str – "DD-MM-YYYY"    if user no date given last trading date is used.
    RETURNS:
        Volume breakdown
    CATEGORY:
        FnO_EOD
    """
    rate_limit()
    # Original: get.fno_eod_participant_wise_vol("17-10-2025")
    return df_to_json(get.fno_eod_participant_wise_vol(date))


@mcp.tool()
def future_historical(symbol: str, type_: str, expiry: str = None, from_date: str = None, to_date: str = None, period: str = None):
    """
    TOOL: future_historical
    DESCRIPTION:
        Historical futures price, volume, OI.
    PARAMETERS:
        symbol: str – "NIFTY", "RELIANCE"
        type_: str – "Index Futures", "Stock Futures"
        expiry: str – "OCT-25", "28-Nov-2025"
        period: str – "1M", "3M", "1Y"
        from_date/to_date: str
    RETURNS:
        Futures time series
    CATEGORY:
        FnO_Historical
    """
    rate_limit()
    # Original: get.future_price_volume_data(...)
    return df_to_json(get.future_price_volume_data(symbol, type_, expiry or period, from_date, to_date))


@mcp.tool()
def option_historical(symbol: str, type_: str, strike: str = None, from_date: str = None, to_date: str = None, expiry: str = None, period: str = None):
    """
    TOOL: option_historical
    DESCRIPTION:
        Historical options price, volume, OI, IV.
    PARAMETERS:
        symbol: str – "NIFTY", "ITC"
        type_: str – "Index Options", "Stock Options"
        strike: str – "47000", "CE", "PE"
        expiry: str – "28-10-2025"
        period: str – "3M", "1Y"
    RETURNS:
        Options time series
    CATEGORY:
        FnO_Historical
    """
    rate_limit()
    # Original: get.option_price_volume_data(...)
    return df_to_json(get.option_price_volume_data(symbol, type_, strike, from_date, to_date, expiry=expiry or period))


@mcp.tool()
def fno_lot_size(symbol: str = None):
    """
    TOOL: fno_lot_size
    DESCRIPTION:
        Current F&O lot sizes (all or specific symbol).
    PARAMETERS:
        symbol: str – Optional, e.g., "TCS"
    RETURNS:
        Lot size data
    CATEGORY:
        FnO_Reference
    """
    rate_limit()
    # Original: get.fno_eom_lot_size("TCS")
    return df_to_json(get.fno_eom_lot_size(symbol))


@mcp.tool()
def fno_business_growth(mode: str = "monthly", month: str = None, year: int = None):
    """
    TOOL: fno_business_growth
    DESCRIPTION:
        F&O segment daily/monthly/yearly turnover growth.
    PARAMETERS:
        mode: str – "daily", "monthly", "yearly"
        month/year: str/int
    RETURNS:
        F&O growth data
    CATEGORY:
        FnO_Stats
    """
    rate_limit()
    # Original: get.fno_dmy_biz_growth(...)
    return df_to_json(get.fno_dmy_biz_growth(mode, month=month, year=year))


@mcp.tool()
def fno_settlement_report(period: str = None, start_year: int = None, end_year: int = None):
    """
    TOOL: fno_settlement_report
    DESCRIPTION:
        F&O monthly settlement statistics by FY.
    PARAMETERS:
        period: str – "2Y", "3Y"
        start_year/end_year: int
    RETURNS:
        F&O settlement data
    CATEGORY:
        FnO_Stats
    """
    rate_limit()
    # Original: get.fno_monthly_settlement_report(...)
    return df_to_json(get.fno_monthly_settlement_report(period or start_year, end_year))


# =====================================================================
#                         SEBI DATA
# =====================================================================

@mcp.tool()
def sebi_circulars(from_date: str = None, to_date: str = None, period: str = None):
    """
    TOOL: sebi_circulars
    DESCRIPTION:
        Latest or historical SEBI circulars.
    PARAMETERS:
        from_date/to_date: str – "DD-MM-YYYY"
        period: str – "1W", "1M", "3M", "1Y"
    RETURNS:
        List of circulars with links
    CATEGORY:
        Regulatory
    """
    rate_limit()
    # Original: get.sebi_circulars(...)
    return df_to_json(get.sebi_circulars(period or from_date, to_date))


@mcp.tool()
def sebi_data_pages(page: int = 1):
    """
    TOOL: sebi_data_pages
    DESCRIPTION:
        Paginated SEBI circulars and orders.
    PARAMETERS:
        page: int – Page number
    RETURNS:
        Circulars for given page
    CATEGORY:
        Regulatory
    """
    rate_limit()
    # Original: get.sebi_data()
    return df_to_json(get.sebi_data(page))


@mcp.tool()
def nifty_chart(timeframe: str = "1D"):
    """
    TOOL: nifty_chart

    DESCRIPTION:
        Retrieves intraday or historical price chart data for the NIFTY 50 index 
        based on the selected timeframe.  
        The tool internally connects to the NSE Next-API `getGraphChart` endpoint,
        handles cookie/session rotation automatically, and normalizes the response 
        into a clean DataFrame before converting it to JSON.

    PARAMETERS:
        timeframe (str):
            Defines the chart duration or lookback period.
            Examples:
                "1D" – 1-day intraday chart 
                "1M" – 1-month chart  
                "3M" – 3-month chart  
                "6M" – 6-month chart  
                "1Y" – 1-year historical chart  
            note: The NSE server will return only the valid supported timeframes.

    RETURNS:
        JSON chart data containing:
            - datetime_utc (string): Timestamp in UTC formatted as "%Y-%m-%d %H:%M:%S"
            - price (float): Index price at that timestamp
            - flag (string): Event marker provided by NSE (e.g., "PO"- Pre Open Market, "NM"- Normal Market, etc.) 

    CATEGORY:
        ChartData
        (All market chart–related tools fall under this category.)
    """
    rate_limit()
    return df_to_json(get.nifty_chart(timeframe))


@mcp.tool()
def stock_chart(symbol: str, timeframe: str = "1D"):
    """
    TOOL: stock_chart

    DESCRIPTION:
        Retrieves intraday or historical price chart data for the stock 
        based on the selected timeframe.  
        The tool internally connects to the NSE Next-API `getGraphChart` endpoint,
        handles cookie/session rotation automatically, and normalizes the response 
        into a clean DataFrame before converting it to JSON.

    PARAMETERS:
        timeframe (str):
            Defines the chart duration or lookback period.
            Examples:
                "1D" – 1-day intraday chart 
                "1W" – 1-week chart 
                "1M" – 1-month chart  
                "1Y" – 1-year historical chart  
            note: The NSE server will return only the valid supported timeframes.

    RETURNS:
        JSON chart data containing:
            - datetime_utc (string): Timestamp in UTC formatted as "%Y-%m-%d %H:%M:%S"
            - price (float): stock price at that timestamp
            - flag (string): Event marker provided by NSE (e.g., "PO"- Pre Open Market, "NM"- Normal Market, etc.) 

    CATEGORY:
        ChartData
        (All market chart–related tools fall under this category.)
    """
    rate_limit()
    return df_to_json(get.stock_chart(symbol, timeframe))


@mcp.tool()
def symbol_full_fno_live_data(symbol: str):
    """
    TOOL: symbol_full_fno_live_data
    DESCRIPTION:
        Fetches complete live FnO data for the specified stock or index.
        Includes all available Futures & Options contracts, identifiers,
        last traded price, volume, open interest, and other key market metrics.

    PARAMETERS:
        symbol: str – Example: "NIFTY", "BANKNIFTY", "RELIANCE"

    RETURNS:
        Dict containing full live FnO chain with identifiers for all
        Futures and Options contracts.

    CATEGORY:
        symbol_fno_live_data
    """
    rate_limit()
    return get.symbol_full_fno_live_data(symbol)


@mcp.tool()
def symbol_specific_most_active_Calls_or_Puts_or_Contracts_by_OI(symbol: str, type_mode: str):
    """
    TOOL: symbol_specific_most_active_Calls_or_Puts_or_Contracts_by_OI
    DESCRIPTION:
        Fetches the Most Active CALLS, PUTS, or CONTRACTS based on Open Interest
        for a specific stock or index.

    PARAMETERS:
        symbol: str – Example: "NIFTY", "RELIANCE"
        type_mode: str – Allowed:
            "CALLS"      → Most Active Call Options by OI
            "PUTS"       → Most Active Put Options by OI
            "CONTRACTS"  → Most Active Combined Contracts by OI

    RETURNS:
        List / dict of the most active FnO contracts based on Open Interest.

    CATEGORY:
        symbol_fno_live_data
    """
    rate_limit()
    return get.symbol_specific_most_active_Calls_or_Puts_or_Contracts_by_OI(symbol, type_mode)


@mcp.tool()
def identifier_based_fno_contracts_live_chart_data(identifier: str):
    """
    TOOL: identifier_based_fno_contracts_live_chart_data
    DESCRIPTION:
        Fetches intraday price chart data (timestamp, price, flag)
        for a specific Futures or Options contract using its NSE identifier.

    PARAMETERS:
        identifier: str – Examples:
            "OPTSTKTCS30-12-2025CE3300.00"
            "FUTSTKTCS30-12-2025XX0.00"
            "FUTIDXNIFTY30-12-2025XX0.00"
            "OPTIDXNIFTY09-12-2025PE25800.00"

        (To find valid identifiers, use:
            symbol_full_fno_live_data
            symbol_specific_most_active_Calls_or_Puts_or_Contracts_by_OI
        )

    RETURNS:
        Intraday price chart data for the specific FnO contract.

    CATEGORY:
        symbol_fno_live_data
    """
    rate_limit()
    return get.identifier_based_fno_contracts_live_chart_data(identifier)


# # Run with streamable HTTP transport
# if __name__ == "__main__":
#     mcp.run(transport="streamable-http")

def main() -> None:
    mcp.run()