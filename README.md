# TWS and Schwab Stock App

A comprehensive trading application that integrates Interactive Brokers TWS (Trader Workstation) and Charles Schwab accounts for stock trading, market data analysis, and portfolio management.

## Prerequisites

Before running the application, ensure you have:

- **Interactive Broker's TWS** installed and running on your desktop
- **Active Schwab account** with API access enabled

> ⚠️ **Note**: Outside of pre-market and after-hours trading sessions, the app may not behave as expected.

## Getting Started

### Authentication

When you first start the program, you'll see an authorization window. Refresh tokens are required for proper authentication and must be obtained:

- On your first login
- Every 7 days when they expire (a timer indicates when this will happen)

If already authorized, click **"Continue Without Auth"** to access the program immediately.

#### Authentication Steps

1. Click **"Click here to authorize"**
2. Log into your Schwab account
3. Agree to the API access agreement
4. Select the Schwab account you want to connect and confirm
5. Copy the URL from the broken webpage and paste it into the Trading App GUI input box
   > ⚠️ The authorization link is only valid for a short window - repeat the process if it expires
6. Click **"Complete Authorization"**

### Navigation

Use the navigation bar in the top left of the GUI to switch between:
- Interactive Brokers trading account
- Schwab trading account

> 📝 **Note**: Loading the Interactive Brokers window takes longer than the Schwab window.

## Schwab Window Features

### Real-Time Stock Data

1. Enter a valid stock ticker symbol (AAPL, TSLA, GE, etc.)
2. Click **"Retrieve Quotes"**
3. View real-time price and volume data feed

### Stock Order Previews

> ⚠️ **Important**: Schwab API doesn't provide paper trading endpoints, so only order previews are available.

1. Enter a valid stock ticker symbol
2. Click **"Search"**
3. If valid, prices update showing last, ask, and bid prices
4. Enter the quantity you wish to purchase/sell
5. Select order type:
   - **Market Order**
   - **Limit Order** (enter desired execution price)
6. Click **"Sell"** or **"Buy"**:
   - **Sell**: Executes at current bid price (or limit price)
   - **Buy**: Executes at current ask price (or limit price)
7. View Order Details overview (status shows REJECTED if account funds are empty)

### Order History Preview

View all previous preview orders. These can be deleted without consequences since they're preview-only.

### Stock Price History Graph

Display price history with your order positions marked on the graph.

1. Enter a valid stock ticker symbol
2. Select time period (past 10 days, 3 days, etc.)
3. Select candlestick interval (every 30 min, 10 min, etc.)
4. Click **"Create Graph"**

### Schwab's Top Movers

View top 10 daily movers with sorting options, displaying:
- Company name
- Symbol
- Last price
- Net change
- Net percent change
- Volume
- Market share

1. Select sorting attribute
2. Select frequency (most recent, past 10 min, past 30 min, etc.)
3. Click **"Find Top Movers"**

## TWS Window Features

> 📝 **Note**: Dropdowns under Buy/Sell Stocks, Stock Data, and Market Data Graphs are synchronized.

### Stock Data Viewing

> ⚠️ **Data Delay**: All data displays with a 15-minute delay unless you have a real-time data subscription.

1. Input stock ticker or select from dropdown
2. View these metrics:
   - Last price
   - Price change vs. open
   - Today's volume
   - Bid/Ask prices
   - Daily high/low

### Stock Order Placement

1. Input or select stock ticker (NASDAQ and NYSE supported)
2. Choose order type:
   - **MKT** (Market)
   - **LMT** (Limit) - enter desired limit price
3. Enter stock quantity
4. Select Buy or Sell
5. **Optional**: Attach bracket orders
   - Set profit taker price or percentage
   - Set stop loss price or percentage
   - Click **"Attach Bracket"** or **"Remove Bracket"**
6. Click **"Submit Order"**
   - **Market hours**: Order placed immediately
   - **Pre/Post market**: Order status becomes "PreSubmitted"

### Order Activity

#### Active Orders
- View PreSubmitted orders, pending Limit orders, and bracket orders
- Cancel orders anytime by clicking **"Cancel"**

#### Completed Orders
- View all completed orders for the day, including cancelled orders

### Price History Graphs

1. Input or select stock ticker
2. Select time period (past 7 days, 1 day, 1 hour, etc.)
3. Select candlestick interval (every 3 hours, 10 min, 30 sec, etc.)

Graphs support full interaction including zoom and pan functionality.

### Stock News

Search for news by individual stock symbol or portfolio-based news.

#### Individual Stock Search:
1. Enter valid stock symbol
2. Click **"Search"**

#### Portfolio News:
1. Click **"View Portfolio News"**

Double-click any article to view full text in a pop-up dialog.

### Portfolio Management

#### Portfolio Overview:
- Total available funds
- Daily potential profits/loss
- Total realized profit/loss
- Total unrealized profit/loss

#### Individual Stock Positions:
- Number of positions owned
- Current combined market value
- Average purchase price
- Last stock price
- Price change since open

**Portfolio Liquidation**: Click **"Liquidate Portfolio"** and confirm to sell all positions.

### Market Scanners

Switch from Portfolio to Market Scanner tab to access scanning tools.

#### Creating a Market Scanner:

1. **Select Scanner Category**:
   - Top % Gainers
   - Hot Contracts by Volume (Relative Volume)

2. **Add Filter Tags** (optional):
   - Select filter from dropdown:
     - Price Above
     - EMA ___ Above
     - MACD Above
   - Input filter value
   - Click **"Add Tag to Screener"**
   - Repeat for additional filters
   - Use **"Clear Tags"** to remove all filters

3. **Create Scanner**: Click **"Create Market Scanner"**

#### Scanner Management:
- Up to 10 active scanners simultaneously
- Each scanner displays up to 50 stocks with symbol, volume, and price change
- Switch between scanners using tabs
- Close scanners by clicking the "X" on tabs
- Scanner information and active filters shown on the right

> ⚠️ **Performance Note**: More active scanners may reduce performance due to TWS rate limits.

## Support

For technical issues or questions about the application, please contact the development team or refer to your broker's API documentation for account-specific concerns.
