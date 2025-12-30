"""
Parallel Agent Executor with Error Handling and Retry Logic
Executes all 5 agents concurrently with graceful degradation
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Raised when comprehensive_data is missing required fields"""
    pass


class AgentExecutionError(Exception):
    """Custom exception for agent execution failures"""
    def __init__(self, agent_name: str, error: Exception):
        self.agent_name = agent_name
        self.error = error
        super().__init__(f"{agent_name} failed: {str(error)}")


class ParallelAgentExecutor:
    """
    Executes agents in parallel with error handling and retry logic

    Features:
    - Concurrent agent execution (5x faster)
    - Automatic retry with exponential backoff
    - Graceful degradation (continues if some agents fail)
    - Detailed error tracking and logging
    - Performance monitoring
    """

    def __init__(
        self,
        fundamentals_agent,
        momentum_agent,
        quality_agent,
        sentiment_agent,
        institutional_flow_agent,
        max_retries: int = 3,
        timeout_seconds: int = 30
    ):
        self.fundamentals_agent = fundamentals_agent
        self.momentum_agent = momentum_agent
        self.quality_agent = quality_agent
        self.sentiment_agent = sentiment_agent
        self.institutional_flow_agent = institutional_flow_agent
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

        logger.info(
            f"ParallelAgentExecutor initialized with 5 agents (max_retries={max_retries}, "
            f"timeout={timeout_seconds}s)"
        )

    def _validate_comprehensive_data(self, symbol: str, data: Dict) -> None:
        """
        Validate that comprehensive_data contains all required fields

        Args:
            symbol: Stock symbol being analyzed
            data: Comprehensive data from provider

        Raises:
            DataValidationError: If required fields are missing
        """
        required_fields = {
            'historical_data': 'Price and volume history (DataFrame)',
            'technical_data': 'Technical indicators (Dict)',
            'info': 'Company information (Dict)'
        }

        missing_fields = []
        invalid_fields = []

        for field, description in required_fields.items():
            if field not in data:
                missing_fields.append(f"{field} ({description})")
            elif data[field] is None:
                invalid_fields.append(f"{field} is None")
            elif field == 'historical_data' and len(data[field]) == 0:
                invalid_fields.append(f"{field} is empty")

        error_messages = []
        if missing_fields:
            error_messages.append(f"Missing fields: {', '.join(missing_fields)}")
        if invalid_fields:
            error_messages.append(f"Invalid fields: {', '.join(invalid_fields)}")

        if error_messages:
            error_msg = f"Data validation failed for {symbol}: {'; '.join(error_messages)}"
            logger.error(error_msg)
            raise DataValidationError(error_msg)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def _execute_agent_with_retry(
        self,
        agent_func,
        agent_name: str,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a single agent with retry logic

        Args:
            agent_func: The agent's analyze method
            agent_name: Name of the agent (for logging)
            *args: Arguments to pass to agent
            **kwargs: Keyword arguments to pass to agent

        Returns:
            Agent result dict with score, confidence, metrics, reasoning
        """
        try:
            # Run agent in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, agent_func, *args),
                timeout=self.timeout_seconds
            )

            # Validate result
            if not isinstance(result, dict):
                raise ValueError(f"{agent_name} returned non-dict result")

            if 'score' not in result or 'confidence' not in result:
                raise ValueError(f"{agent_name} missing required fields")

            logger.info(
                f"✅ {agent_name} completed: score={result.get('score', 0):.1f}, "
                f"confidence={result.get('confidence', 0):.2f}"
            )

            return result

        except asyncio.TimeoutError:
            logger.error(f"⏱️ {agent_name} timed out after {self.timeout_seconds}s")
            raise AgentExecutionError(agent_name, TimeoutError("Agent timeout"))

        except Exception as e:
            logger.error(f"❌ {agent_name} failed: {str(e)}")
            raise AgentExecutionError(agent_name, e)

    def _create_fallback_result(self, agent_name: str, error: Exception) -> Dict[str, Any]:
        """
        Create fallback result when agent fails after all retries

        Returns neutral score with low confidence
        """
        return {
            'score': 50.0,  # Neutral score
            'confidence': 0.0,  # Zero confidence
            'metrics': {},
            'reasoning': f"Agent failed: {str(error)[:100]}",
            'error': str(error),
            'failed': True
        }

    async def execute_all_agents(
        self,
        symbol: str,
        comprehensive_data: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute all 5 agents in parallel with error handling

        Args:
            symbol: Stock ticker symbol
            comprehensive_data: Market data from EnhancedYahooProvider

        Returns:
            Dict with results from all agents (may include fallback results for failed agents)
        """
        start_time = time.time()
        logger.info(f"🚀 Starting parallel execution for {symbol}")

        # Validate comprehensive_data before proceeding
        try:
            self._validate_comprehensive_data(symbol, comprehensive_data)
            logger.info(f"✅ Data validation passed for {symbol}")
        except DataValidationError as e:
            logger.error(f"Data validation failed: {e}")
            # Return fallback results for all agents if data is invalid
            return {
                'fundamentals': self._create_fallback_result('Fundamentals', e),
                'momentum': self._create_fallback_result('Momentum', e),
                'quality': self._create_fallback_result('Quality', e),
                'sentiment': self._create_fallback_result('Sentiment', e),
                'institutional_flow': self._create_fallback_result('InstitutionalFlow', e)
            }

        # Create tasks for all 5 agents
        tasks = {
            'fundamentals': self._execute_agent_with_retry(
                self.fundamentals_agent.analyze,
                'Fundamentals',
                symbol
            ),
            'momentum': self._execute_agent_with_retry(
                self.momentum_agent.analyze,
                'Momentum',
                symbol,
                comprehensive_data['historical_data'],
                comprehensive_data['historical_data']
            ),
            'quality': self._execute_agent_with_retry(
                lambda s: self.quality_agent.analyze(s, cached_data=comprehensive_data),
                'Quality',
                symbol
            ),
            'sentiment': self._execute_agent_with_retry(
                self.sentiment_agent.analyze,
                'Sentiment',
                symbol
            ),
            'institutional_flow': self._execute_agent_with_retry(
                lambda s: self.institutional_flow_agent.analyze(
                    s,
                    comprehensive_data['historical_data'],
                    cached_data=comprehensive_data
                ),
                'InstitutionalFlow',
                symbol
            )
        }

        # Execute all agents concurrently
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        # Process results and handle failures
        agent_results = {}
        failed_agents = []

        for agent_name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.warning(f"⚠️ {agent_name} failed permanently, using fallback")
                agent_results[agent_name] = self._create_fallback_result(agent_name, result)
                failed_agents.append(agent_name)
            else:
                agent_results[agent_name] = result

        # Calculate execution time
        execution_time = time.time() - start_time

        # Log summary
        success_count = len(agent_results) - len(failed_agents)
        logger.info(
            f"✨ Parallel execution completed in {execution_time:.2f}s "
            f"({success_count}/5 agents succeeded)"
        )

        if failed_agents:
            logger.warning(f"⚠️ Failed agents: {', '.join(failed_agents)}")

        # Add metadata
        agent_results['_meta'] = {
            'execution_time': execution_time,
            'failed_agents': failed_agents,
            'success_count': success_count,
            'total_agents': 5,
            'timestamp': datetime.now().isoformat()
        }

        return agent_results

    async def execute_batch(
        self,
        symbols: List[str],
        data_provider
    ) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Execute analysis for multiple symbols in parallel

        Args:
            symbols: List of stock symbols
            data_provider: EnhancedYahooProvider instance

        Returns:
            Dict mapping symbols to their agent results
        """
        logger.info(f"🎯 Starting batch parallel execution for {len(symbols)} symbols")
        start_time = time.time()

        # Create tasks for all symbols
        async def analyze_symbol(symbol: str):
            try:
                # Get market data
                comprehensive_data = await asyncio.to_thread(
                    data_provider.get_comprehensive_data,
                    symbol
                )

                if 'error' in comprehensive_data:
                    raise ValueError(f"No data available for {symbol}")

                # Execute agents in parallel
                results = await self.execute_all_agents(symbol, comprehensive_data)
                return symbol, results

            except Exception as e:
                logger.error(f"❌ Batch analysis failed for {symbol}: {e}")
                return symbol, {
                    '_meta': {
                        'error': str(e),
                        'failed': True
                    }
                }

        # Execute all symbols concurrently
        tasks = [analyze_symbol(symbol) for symbol in symbols]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        # Build results dict
        batch_results = {}
        for result in results_list:
            if isinstance(result, Exception):
                logger.error(f"Batch task failed: {result}")
                continue
            symbol, agent_results = result
            batch_results[symbol] = agent_results

        execution_time = time.time() - start_time
        logger.info(
            f"✅ Batch parallel execution completed in {execution_time:.2f}s "
            f"({len(batch_results)}/{len(symbols)} symbols processed)"
        )

        return batch_results

    def get_system_health(self) -> Dict[str, Any]:
        """
        Check health of all agents

        Returns:
            Dict with health status of each agent
        """
        health_status = {
            'fundamentals': 'unknown',
            'momentum': 'unknown',
            'quality': 'unknown',
            'sentiment': 'unknown',
            'institutional_flow': 'unknown',
            'overall': 'unknown'
        }

        try:
            # Try to execute all agents with AAPL as test
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, can't run
                return health_status

            # Quick health check (no retries)
            results = loop.run_until_complete(
                self._quick_health_check()
            )

            health_status = results

        except Exception as e:
            logger.error(f"Health check failed: {e}")

        return health_status

    async def _quick_health_check(self) -> Dict[str, str]:
        """Quick health check without retries"""
        test_symbol = "AAPL"

        async def check_agent(agent_func, agent_name):
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(agent_func, test_symbol),
                    timeout=5
                )
                return 'healthy'
            except:
                return 'unhealthy'

        results = await asyncio.gather(
            check_agent(self.fundamentals_agent.analyze, 'fundamentals'),
            check_agent(lambda s: self.momentum_agent.analyze(s, None, None), 'momentum'),
            check_agent(lambda s: self.quality_agent.analyze(s, {}), 'quality'),
            check_agent(self.sentiment_agent.analyze, 'sentiment'),
            check_agent(lambda s: self.institutional_flow_agent.analyze(s, None, {}), 'institutional_flow'),
            return_exceptions=True
        )

        health = {
            'fundamentals': results[0] if not isinstance(results[0], Exception) else 'unhealthy',
            'momentum': results[1] if not isinstance(results[1], Exception) else 'unhealthy',
            'quality': results[2] if not isinstance(results[2], Exception) else 'unhealthy',
            'sentiment': results[3] if not isinstance(results[3], Exception) else 'unhealthy',
            'institutional_flow': results[4] if not isinstance(results[4], Exception) else 'unhealthy',
        }

        healthy_count = sum(1 for status in health.values() if status == 'healthy')
        health['overall'] = 'healthy' if healthy_count >= 4 else 'degraded' if healthy_count >= 3 else 'unhealthy'

        return health
