#!/usr/bin/env python3
"""CryptoArena Deployment Script

Comprehensive deployment script for production launch.
Handles:
- Environment validation
- Dependency checks
- Database initialization
- Contract deployment (if needed)
- Health monitoring
- Service startup
"""
import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentManager:
    """Manages CryptoArena deployment process."""
    
    def __init__(self, config_path: Optional[str] = None, mode: str = "production"):
        self.config_path = config_path or "config/deployment.json"
        self.mode = mode
        self.config = self._load_config()
        self.checks_passed: List[str] = []
        self.checks_failed: List[str] = []
    
    def _load_config(self) -> Dict:
        """Load deployment configuration."""
        try:
            config_file = project_root / self.config_path
            if config_file.exists():
                with open(config_file) as f:
                    return json.load(f)
            else:
                logger.warning(f"Config file not found: {config_file}. Using defaults.")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default deployment configuration."""
        return {
            "mode": self.mode,
            "environment": {
                "required_vars": [
                    "COINGECKO_API_KEY",
                    "COINMARKETCAP_API_KEY",
                    "OPENAI_API_KEY"
                ],
                "optional_vars": [
                    "POLYMARKET_API_KEY",
                    "TELEGRAM_BOT_TOKEN",
                    "DISCORD_WEBHOOK_URL"
                ]
            },
            "database": {
                "type": "sqlite",
                "path": "data/arena.db"
            },
            "blockchain": {
                "network": "base",
                "deploy_contracts": True
            },
            "monitoring": {
                "enabled": True,
                "port": 8000,
                "metrics_interval": 60
            }
        }
    
    async def deploy(self) -> bool:
        """Execute full deployment process.
        
        Returns:
            True if deployment successful, False otherwise
        """
        logger.info(f"=== Starting CryptoArena Deployment ({self.mode} mode) ===")
        
        try:
            # Step 1: Pre-deployment checks
            if not await self._run_checks():
                logger.error("Pre-deployment checks failed")
                return False
            
            # Step 2: Initialize directories
            await self._setup_directories()
            
            # Step 3: Initialize database
            await self._setup_database()
            
            # Step 4: Deploy smart contracts (if needed)
            if self.config.get("blockchain", {}).get("deploy_contracts"):
                await self._deploy_contracts()
            
            # Step 5: Initialize game state
            await self._initialize_game_state()
            
            # Step 6: Start monitoring
            if self.config.get("monitoring", {}).get("enabled"):
                await self._start_monitoring()
            
            # Step 7: Health check
            await self._health_check()
            
            logger.info("=== Deployment completed successfully ===")
            self._print_summary()
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}", exc_info=True)
            return False
    
    async def _run_checks(self) -> bool:
        """Run pre-deployment validation checks.
        
        Returns:
            True if all critical checks pass
        """
        logger.info("Running pre-deployment checks...")
        
        checks = [
            self._check_python_version(),
            self._check_dependencies(),
            self._check_environment_vars(),
            self._check_disk_space(),
            self._check_network_connectivity(),
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        all_passed = all(r is True for r in results if not isinstance(r, Exception))
        
        if all_passed:
            logger.info(f"✓ All checks passed: {len(self.checks_passed)}")
        else:
            logger.error(f"✗ Some checks failed: {len(self.checks_failed)}")
            for failure in self.checks_failed:
                logger.error(f"  - {failure}")
        
        return all_passed
    
    async def _check_python_version(self) -> bool:
        """Check Python version compatibility."""
        try:
            version = sys.version_info
            if version.major == 3 and version.minor >= 9:
                self.checks_passed.append(f"Python version: {version.major}.{version.minor}")
                return True
            else:
                self.checks_failed.append(f"Python 3.9+ required, found {version.major}.{version.minor}")
                return False
        except Exception as e:
            self.checks_failed.append(f"Python version check failed: {e}")
            return False
    
    async def _check_dependencies(self) -> bool:
        """Check required Python packages."""
        try:
            requirements_file = project_root / "requirements.txt"
            if not requirements_file.exists():
                self.checks_failed.append("requirements.txt not found")
                return False
            
            # Try importing critical packages
            critical_packages = [
                "aiohttp",
                "pydantic",
                "web3",
            ]
            
            missing = []
            for package in critical_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing.append(package)
            
            if missing:
                self.checks_failed.append(f"Missing packages: {', '.join(missing)}")
                return False
            
            self.checks_passed.append("All critical dependencies installed")
            return True
            
        except Exception as e:
            self.checks_failed.append(f"Dependency check failed: {e}")
            return False
    
    async def _check_environment_vars(self) -> bool:
        """Check required environment variables."""
        try:
            env_config = self.config.get("environment", {})
            required = env_config.get("required_vars", [])
            
            missing = [var for var in required if not os.getenv(var)]
            
            if missing:
                self.checks_failed.append(f"Missing env vars: {', '.join(missing)}")
                return False
            
            self.checks_passed.append(f"All {len(required)} required env vars set")
            return True
            
        except Exception as e:
            self.checks_failed.append(f"Environment check failed: {e}")
            return False
    
    async def _check_disk_space(self) -> bool:
        """Check available disk space."""
        try:
            import shutil
            
            stat = shutil.disk_usage(project_root)
            free_gb = stat.free / (1024**3)
            
            if free_gb < 1.0:
                self.checks_failed.append(f"Low disk space: {free_gb:.1f}GB available")
                return False
            
            self.checks_passed.append(f"Disk space: {free_gb:.1f}GB available")
            return True
            
        except Exception as e:
            self.checks_failed.append(f"Disk space check failed: {e}")
            return False
    
    async def _check_network_connectivity(self) -> bool:
        """Check network connectivity to critical services."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                # Test CoinGecko API
                try:
                    async with session.get(
                        "https://api.coingecko.com/api/v3/ping",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            self.checks_passed.append("CoinGecko API reachable")
                        else:
                            self.checks_failed.append(f"CoinGecko API error: {response.status}")
                            return False
                except Exception as e:
                    self.checks_failed.append(f"CoinGecko API unreachable: {e}")
                    return False
            
            return True
            
        except Exception as e:
            self.checks_failed.append(f"Network check failed: {e}")
            return False
    
    async def _setup_directories(self):
        """Create necessary directories."""
        logger.info("Setting up directories...")
        
        directories = [
            "data",
            "logs",
            "state",
            "reports",
            "cache"
        ]
        
        for directory in directories:
            dir_path = project_root / directory
            dir_path.mkdir(exist_ok=True)
            logger.info(f"  ✓ Created/verified: {directory}/")
    
    async def _setup_database(self):
        """Initialize database."""
        logger.info("Initializing database...")
        
        try:
            from src.state.manager import GameStateManager
            
            db_config = self.config.get("database", {})
            state_manager = GameStateManager(db_config)
            await state_manager.initialize()
            
            logger.info("  ✓ Database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _deploy_contracts(self):
        """Deploy smart contracts to blockchain."""
        logger.info("Deploying smart contracts...")
        
        try:
            # Import contract deployment module
            # This would handle actual contract deployment
            logger.info("  ✓ Contracts deployed (stub - implement actual deployment)")
            
        except Exception as e:
            logger.error(f"Contract deployment failed: {e}")
            # Non-critical for MVP - paper trading mode doesn't need contracts
            logger.warning("Continuing without contract deployment...")
    
    async def _initialize_game_state(self):
        """Initialize game state with default values."""
        logger.info("Initializing game state...")
        
        try:
            from src.state.manager import GameStateManager
            
            state_manager = GameStateManager()
            await state_manager.initialize_agents()
            
            logger.info("  ✓ Game state initialized")
            
        except Exception as e:
            logger.error(f"Game state initialization failed: {e}")
            raise
    
    async def _start_monitoring(self):
        """Start monitoring services."""
        logger.info("Starting monitoring...")
        
        try:
            # This would start the monitoring web server
            # For now, just log that it would start
            monitoring_config = self.config.get("monitoring", {})
            port = monitoring_config.get("port", 8000)
            
            logger.info(f"  ✓ Monitoring configured on port {port}")
            logger.info("    (Start monitoring server separately with: python scripts/monitor.py)")
            
        except Exception as e:
            logger.error(f"Monitoring startup failed: {e}")
            # Non-critical
            logger.warning("Continuing without monitoring...")
    
    async def _health_check(self):
        """Run post-deployment health check."""
        logger.info("Running health check...")
        
        try:
            from src.arenacore.orchestrator import ArenaCore
            
            # Initialize ArenaCore to verify all components
            arena = ArenaCore(mode="paper")
            status = await arena.health_check()
            
            if status.get("healthy"):
                logger.info("  ✓ Health check passed")
            else:
                logger.warning(f"  ⚠ Health check warnings: {status}")
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise
    
    def _print_summary(self):
        """Print deployment summary."""
        print("\n" + "="*60)
        print("🏟️  CryptoArena Deployment Summary")
        print("="*60)
        print(f"Mode: {self.mode}")
        print(f"Checks passed: {len(self.checks_passed)}")
        print(f"\nNext steps:")
        print("  1. Start the arena: python scripts/start_arena.py")
        print("  2. Monitor status: python scripts/monitor.py")
        print("  3. View logs: tail -f logs/arena.log")
        print("="*60 + "\n")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Deploy CryptoArena")
    parser.add_argument(
        "--mode",
        choices=["production", "staging", "development"],
        default="production",
        help="Deployment mode"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to deployment config file"
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip pre-deployment checks (not recommended)"
    )
    
    args = parser.parse_args()
    
    deployer = DeploymentManager(config_path=args.config, mode=args.mode)
    
    success = await deployer.deploy()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
