#!/usr/bin/env python3
"""CryptoArena Health Check & Diagnostics

Comprehensive system health monitoring and diagnostics.
Checks all critical components and reports status.
"""
import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthChecker:
    """System health checker for CryptoArena."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.checks: List[Dict] = []
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.start_time = datetime.now()
    
    async def run_all_checks(self) -> Dict:
        """Run all health checks and return comprehensive status.
        
        Returns:
            Dictionary with health status and details
        """
        logger.info("🔍 Starting CryptoArena health check...")
        
        checks = [
            ("System Resources", self._check_system_resources()),
            ("Environment Variables", self._check_environment()),
            ("API Connectivity", self._check_api_connectivity()),
            ("Database", self._check_database()),
            ("File System", self._check_filesystem()),
            ("Dependencies", self._check_dependencies()),
            ("Game State", self._check_game_state()),
            ("Agents", self._check_agents()),
            ("Recent Activity", self._check_recent_activity()),
        ]
        
        for check_name, check_coro in checks:
            try:
                logger.info(f"Checking: {check_name}...")
                status, details = await check_coro
                
                self.checks.append({
                    "name": check_name,
                    "status": status,
                    "details": details,
                    "timestamp": datetime.now().isoformat()
                })
                
                if status == "ok":
                    logger.info(f"  ✔️ {check_name}: OK")
                elif status == "warning":
                    logger.warning(f"  ⚠️ {check_name}: WARNING - {details}")
                    self.warnings.append(f"{check_name}: {details}")
                else:
                    logger.error(f"  ✗ {check_name}: ERROR - {details}")
                    self.errors.append(f"{check_name}: {details}")
                    
            except Exception as e:
                logger.error(f"  ✗ {check_name}: EXCEPTION - {e}")
                self.errors.append(f"{check_name}: {str(e)}")
                self.checks.append({
                    "name": check_name,
                    "status": "error",
                    "details": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return self._generate_report()
    
    async def _check_system_resources(self) -> Tuple[str, str]:
        """Check system resource availability."""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage(project_root)
            disk_percent = disk.percent
            
            issues = []
            if cpu_percent > 90:
                issues.append(f"High CPU: {cpu_percent}%")
            if memory_percent > 90:
                issues.append(f"High Memory: {memory_percent}%")
            if disk_percent > 90:
                issues.append(f"High Disk: {disk_percent}%")
            
            if issues:
                return "warning", "; ".join(issues)
            
            details = f"CPU: {cpu_percent}%, RAM: {memory_percent}%, Disk: {disk_percent}%"
            return "ok", details
            
        except ImportError:
            return "warning", "psutil not installed - cannot check resources"
        except Exception as e:
            return "error", str(e)
    
    async def _check_environment(self) -> Tuple[str, str]:
        """Check required environment variables."""
        required = [
            "COINGECKO_API_KEY",
            "COINMARKETCAP_API_KEY",
            "OPENAI_API_KEY"
        ]
        
        missing = [var for var in required if not os.getenv(var)]
        
        if missing:
            return "error", f"Missing: {', '.join(missing)}"
        
        # Check optional but recommended
        optional = ["POLYMARKET_API_KEY", "TELEGRAM_BOT_TOKEN"]
        missing_optional = [var for var in optional if not os.getenv(var)]
        
        if missing_optional:
            return "warning", f"Optional missing: {', '.join(missing_optional)}"
        
        return "ok", f"All {len(required)} required variables set"
    
    async def _check_api_connectivity(self) -> Tuple[str, str]:
        """Check connectivity to external APIs."""
        try:
            import aiohttp
            
            apis_to_check = [
                ("CoinGecko", "https://api.coingecko.com/api/v3/ping"),
                ("CoinMarketCap", "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=1"),
            ]
            
            results = []
            async with aiohttp.ClientSession() as session:
                for name, url in apis_to_check:
                    try:
                        headers = {}
                        if name == "CoinMarketCap":
                            api_key = os.getenv("COINMARKETCAP_API_KEY")
                            if api_key:
                                headers["X-CMC_PRO_API_KEY"] = api_key
                        
                        async with session.get(
                            url,
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as response:
                            if response.status < 500:
                                results.append(f"{name}: OK")
                            else:
                                results.append(f"{name}: {response.status}")
                    except asyncio.TimeoutError:
                        results.append(f"{name}: Timeout")
                    except Exception as e:
                        results.append(f"{name}: {str(e)[:30]}")
            
            if all("OK" in r for r in results):
                return "ok", "; ".join(results)
            else:
                return "warning", "; ".join(results)
                
        except ImportError:
            return "error", "aiohttp not installed"
        except Exception as e:
            return "error", str(e)
    
    async def _check_database(self) -> Tuple[str, str]:
        """Check database connectivity and integrity."""
        try:
            db_path = project_root / "data" / "arena.db"
            
            if not db_path.exists():
                return "warning", "Database not initialized"
            
            # Check database size
            size_mb = db_path.stat().st_size / (1024 * 1024)
            
            # Try to connect
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check tables exist
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            if len(tables) == 0:
                return "warning", "Database empty - no tables"
            
            return "ok", f"Size: {size_mb:.2f}MB, Tables: {len(tables)}"
            
        except Exception as e:
            return "error", str(e)
    
    async def _check_filesystem(self) -> Tuple[str, str]:
        """Check required directories and files."""
        required_dirs = ["data", "logs", "state", "config"]
        required_files = ["requirements.txt", ".env.example"]
        
        issues = []
        
        # Check directories
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            if not dir_path.exists():
                issues.append(f"Missing dir: {dir_name}")
            elif not os.access(dir_path, os.W_OK):
                issues.append(f"Not writable: {dir_name}")
        
        # Check files
        for file_name in required_files:
            file_path = project_root / file_name
            if not file_path.exists():
                issues.append(f"Missing file: {file_name}")
        
        if issues:
            return "error", "; ".join(issues)
        
        return "ok", "All directories and files present"
    
    async def _check_dependencies(self) -> Tuple[str, str]:
        """Check Python package dependencies."""
        critical_packages = [
            "aiohttp",
            "pydantic",
            "web3",
            "openai",
        ]
        
        missing = []
        versions = []
        
        for package in critical_packages:
            try:
                mod = __import__(package)
                version = getattr(mod, "__version__", "unknown")
                versions.append(f"{package}=={version}")
            except ImportError:
                missing.append(package)
        
        if missing:
            return "error", f"Missing: {', '.join(missing)}"
        
        return "ok", f"Installed: {len(versions)} packages"
    
    async def _check_game_state(self) -> Tuple[str, str]:
        """Check game state and configuration."""
        try:
            state_file = project_root / "state" / "game_state.json"
            
            if not state_file.exists():
                return "warning", "Game not started yet"
            
            with open(state_file) as f:
                state = json.load(f)
            
            # Check state validity
            required_keys = ["cycle", "portfolio", "agents"]
            missing_keys = [k for k in required_keys if k not in state]
            
            if missing_keys:
                return "error", f"Invalid state - missing: {missing_keys}"
            
            cycle = state.get("cycle", 0)
            portfolio_value = state.get("portfolio", {}).get("total_value", 0)
            
            return "ok", f"Cycle: {cycle}, Portfolio: ${portfolio_value:,.2f}"
            
        except json.JSONDecodeError:
            return "error", "Corrupted game state file"
        except Exception as e:
            return "error", str(e)
    
    async def _check_agents(self) -> Tuple[str, str]:
        """Check agent status and configuration."""
        try:
            from src.agents.crew import AgentCrew
            
            crew = AgentCrew()
            agent_count = len(crew.agents)
            
            if agent_count == 0:
                return "error", "No agents loaded"
            
            # Try to get agent names
            agent_ids = [a.AGENT_ID for a in crew.agents if hasattr(a, 'AGENT_ID')]
            
            return "ok", f"{agent_count} agents active: {', '.join(agent_ids)}"
            
        except ImportError as e:
            return "error", f"Cannot import agents: {e}"
        except Exception as e:
            return "error", str(e)
    
    async def _check_recent_activity(self) -> Tuple[str, str]:
        """Check for recent game activity."""
        try:
            log_file = project_root / "logs" / "arena.log"
            
            if not log_file.exists():
                return "warning", "No log file found - game not started"
            
            # Check last modification time
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            time_since = datetime.now() - mtime
            
            if time_since > timedelta(hours=2):
                return "warning", f"No activity for {time_since.total_seconds()/3600:.1f}h"
            
            # Count recent errors
            with open(log_file, 'r') as f:
                lines = f.readlines()[-100:]  # Last 100 lines
            
            error_count = sum(1 for line in lines if 'ERROR' in line)
            
            if error_count > 10:
                return "warning", f"Last activity: {time_since.seconds//60}m ago, {error_count} recent errors"
            
            return "ok", f"Last activity: {time_since.seconds//60}m ago"
            
        except Exception as e:
            return "error", str(e)
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive health report."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        # Determine overall status
        if self.errors:
            overall_status = "unhealthy"
        elif self.warnings:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        report = {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(elapsed, 2),
            "checks": self.checks,
            "summary": {
                "total_checks": len(self.checks),
                "passed": sum(1 for c in self.checks if c["status"] == "ok"),
                "warnings": len(self.warnings),
                "errors": len(self.errors)
            }
        }
        
        if self.warnings:
            report["warnings"] = self.warnings
        if self.errors:
            report["errors"] = self.errors
        
        return report
    
    def print_report(self, report: Dict):
        """Print formatted health report."""
        print("\n" + "="*60)
        print("🏟️  CryptoArena Health Check Report")
        print("="*60)
        
        status = report["status"].upper()
        status_emoji = {
            "HEALTHY": "✔️",
            "DEGRADED": "⚠️",
            "UNHEALTHY": "✗"
        }.get(status, "?")
        
        print(f"\nOverall Status: {status_emoji} {status}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Duration: {report['duration_seconds']}s")
        
        summary = report["summary"]
        print(f"\nSummary:")
        print(f"  Total Checks: {summary['total_checks']}")
        print(f"  Passed: {summary['passed']}")
        print(f"  Warnings: {summary['warnings']}")
        print(f"  Errors: {summary['errors']}")
        
        if report.get("warnings"):
            print(f"\n⚠️  Warnings:")
            for warning in report["warnings"]:
                print(f"  - {warning}")
        
        if report.get("errors"):
            print(f"\n✗ Errors:")
            for error in report["errors"]:
                print(f"  - {error}")
        
        if self.verbose:
            print(f"\nDetailed Checks:")
            for check in report["checks"]:
                status_icon = {
                    "ok": "✔️",
                    "warning": "⚠️",
                    "error": "✗"
                }.get(check["status"], "?")
                print(f"  {status_icon} {check['name']}: {check['details']}")
        
        print("\n" + "="*60 + "\n")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check CryptoArena system health"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed check results"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save report to file"
    )
    
    args = parser.parse_args()
    
    checker = HealthChecker(verbose=args.verbose)
    report = await checker.run_all_checks()
    
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        checker.print_report(report)
    
    if args.save:
        save_path = Path(args.save)
        with open(save_path, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to: {save_path}")
    
    # Exit code based on health status
    if report["status"] == "unhealthy":
        sys.exit(1)
    elif report["status"] == "degraded":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
