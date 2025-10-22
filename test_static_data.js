// Quick test to verify static data file works
// Run with: node test_static_data.js

const fs = require('fs');
const path = require('path');

const dataFile = path.join(__dirname, 'frontend/src/data/staticBacktestData.ts');

console.log('🔍 Checking static backtest data file...\n');

if (!fs.existsSync(dataFile)) {
  console.error('❌ File not found:', dataFile);
  process.exit(1);
}

const content = fs.readFileSync(dataFile, 'utf8');

// Extract JSON data (everything between [ and ];)
const jsonStart = content.indexOf('= [');
const jsonEnd = content.lastIndexOf('];');

if (jsonStart === -1 || jsonEnd === -1) {
  console.error('❌ Could not find JSON data in file');
  process.exit(1);
}

const jsonContent = content.substring(jsonStart + 2, jsonEnd + 1);

try {
  const data = JSON.parse(jsonContent);

  console.log(`✅ File exists: ${dataFile}`);
  console.log(`✅ Valid JSON: ${data.length} backtests found\n`);

  console.log('📊 Backtest Summary:\n');
  data.forEach((bt, i) => {
    const cagr = bt.metrics.cagr * 100;
    const sharpe = bt.metrics.sharpe_ratio;
    const returnPct = bt.total_return * 100;

    console.log(`${i + 1}. ${bt.start_date} → ${bt.end_date}`);
    console.log(`   Return: ${returnPct > 0 ? '+' : ''}${returnPct.toFixed(2)}%`);
    console.log(`   CAGR: ${cagr > 0 ? '+' : ''}${cagr.toFixed(2)}%`);
    console.log(`   Sharpe: ${sharpe.toFixed(2)}`);
    console.log(`   Equity points: ${bt.equity_curve.length}`);
    console.log(`   Rebalances: ${bt.rebalances}`);
    console.log('');
  });

  console.log('✅ All tests passed! Static data ready for frontend.\n');

} catch (error) {
  console.error('❌ JSON parse error:', error.message);
  process.exit(1);
}
