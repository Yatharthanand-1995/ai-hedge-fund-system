# Stock Analysis Demo - Vercel Deployment

## 🚀 Live Demo

This is a **portfolio showcase deployment** of the AI-Powered Hedge Fund Stock Analysis System.

- **Live URL**: [Your Vercel URL will be here after deployment]
- **Feature**: AI-powered stock analysis of 50 elite stocks
- **Technology**: 5-agent AI system with weighted scoring

## 🏗️ Architecture

- **Frontend**: Deployed on Vercel (Static SPA)
- **Backend**: Runs locally on developer's machine (localhost:8010)

## 👀 For Demo Viewers

This demonstration showcases:

### 5-Agent AI Analysis Framework
1. **Fundamentals Agent (36%)** - Financial health, profitability, growth, and valuation
2. **Momentum Agent (27%)** - Technical analysis and price trend evaluation
3. **Quality Agent (18%)** - Business characteristics and operational efficiency
4. **Sentiment Agent (9%)** - Market sentiment and analyst outlook
5. **Institutional Flow Agent (10%)** - Smart money detection and volume patterns

### Key Features Demonstrated
- ✅ Real-time analysis of 50 elite S&P 100 stocks
- ✅ AI-powered investment recommendations (STRONG BUY to SELL)
- ✅ Comprehensive filtering and sorting capabilities
- ✅ Detailed agent score breakdowns
- ✅ Investment thesis generation with key strengths and risks
- ✅ Market regime detection (Bull/Bear, High/Low volatility)
- ✅ Professional-grade data visualization

### Important Note

**Live Data Dependency**: This demo requires the backend API to be running locally for real-time stock data. When viewing the demo:
- If you see stock data, the API is currently running ✅
- If you see an error message, the API is offline (normal for demos) ⚠️

For a **live demonstration** with real data, please contact the developer.

## 💻 For Developers

### Full Local Setup

To run the complete system locally with all features:

```bash
# Clone repository
git clone <your-repo-url>
cd ai_hedge_fund_system

# Install dependencies and start system
./start_system.sh
```

This will start:
- Backend API on `http://localhost:8010`
- Frontend on `http://localhost:5174`

### Available Features in Full Local Setup
- 📊 Stock Analysis (50 stocks)
- 📈 Portfolio Manager
- 📉 5-Year Backtesting
- 💵 Paper Trading Simulator
- 🔔 System Alerts
- 📚 System Details & Health Monitoring

### Demo vs Full System

| Feature | Vercel Demo | Full Local System |
|---------|-------------|-------------------|
| Stock Analysis | ✅ Visible | ✅ Full Access |
| Dashboard | ❌ Hidden | ✅ Full Access |
| Portfolio Manager | ❌ Hidden | ✅ Full Access |
| Backtesting | ❌ Hidden | ✅ Full Access |
| Paper Trading | ❌ Hidden | ✅ Full Access |
| System Details | ❌ Hidden | ✅ Full Access |

## 🛠️ Technical Stack

**Frontend**:
- React 19 + TypeScript
- Vite build system
- TailwindCSS
- React Query for state management
- Recharts for visualizations

**Backend** (Local Only):
- Python 3.9+ with FastAPI
- yfinance for market data
- TA-Lib for technical indicators
- Multi-agent AI system
- Narrative generation engine

## 📚 Documentation

For complete documentation, API reference, and setup instructions:
- See the main [README.md](./README.md) in the repository

## 🔗 Links

- **GitHub Repository**: [Your repo URL]
- **API Documentation**: Available when running locally at `http://localhost:8010/docs`
- **Portfolio**: [Your portfolio URL]

## 📧 Contact

For questions, live demonstrations, or collaboration opportunities:
- **Developer**: [Your name]
- **Email**: [Your email]
- **LinkedIn**: [Your LinkedIn]

---

**Note**: This demo deployment is configured to show only the Stock Analysis feature. The complete system includes additional features for portfolio management, backtesting, paper trading, and automated monitoring available in the full local setup.
