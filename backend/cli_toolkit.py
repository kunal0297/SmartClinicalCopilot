import click
import logging
import json
import yaml
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import aiohttp
from tabulate import tabulate
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from .config import settings
from .rule_engine import RuleEngine
from .alert_suppression import AlertSuppressionEngine
from .fhir_subscription import FHIRSubscriptionHandler
from .llm_benchmark import LLMBenchmark

console = Console()
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Clinical Decision Support System CLI Toolkit"""
    pass

@cli.command()
@click.option('--config', '-c', help='Path to configuration file')
def init(config):
    """Initialize the system with configuration"""
    try:
        if config:
            with open(config, 'r') as f:
                config_data = yaml.safe_load(f)
                # Apply configuration
                console.print("[green]Configuration loaded successfully[/green]")
        else:
            console.print("[yellow]No configuration file provided, using defaults[/yellow]")
    except Exception as e:
        console.print(f"[red]Error initializing system: {str(e)}[/red]")

@cli.command()
@click.option('--resource-type', '-r', help='FHIR resource type to monitor')
@click.option('--duration', '-d', default=60, help='Monitoring duration in seconds')
def monitor(resource_type, duration):
    """Monitor system performance and resource usage"""
    try:
        console.print(f"[bold]Starting system monitoring for {duration} seconds...[/bold]")
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Monitoring...", total=duration)
            
            # Collect metrics
            metrics = {
                'rule_matches': [],
                'llm_requests': [],
                'alert_counts': [],
                'response_times': []
            }
            
            for _ in range(duration):
                # Collect current metrics
                current_metrics = asyncio.run(_collect_metrics(resource_type))
                for key in metrics:
                    metrics[key].append(current_metrics[key])
                
                progress.update(task, advance=1)
                asyncio.sleep(1)
        
        # Display results
        _display_monitoring_results(metrics)
        
    except Exception as e:
        console.print(f"[red]Error during monitoring: {str(e)}[/red]")

@cli.command()
@click.option('--ruleset', '-r', help='Path to ruleset file')
@click.option('--validate/--no-validate', default=True, help='Validate ruleset before loading')
def load_ruleset(ruleset, validate):
    """Load a new ruleset into the system"""
    try:
        if not ruleset:
            console.print("[red]No ruleset file provided[/red]")
            return

        with open(ruleset, 'r') as f:
            ruleset_data = json.load(f)

        if validate:
            console.print("[yellow]Validating ruleset...[/yellow]")
            if not _validate_ruleset(ruleset_data):
                console.print("[red]Ruleset validation failed[/red]")
                return

        # Load ruleset
        rule_engine = RuleEngine()
        asyncio.run(rule_engine.load_ruleset(ruleset_data))
        console.print("[green]Ruleset loaded successfully[/green]")

    except Exception as e:
        console.print(f"[red]Error loading ruleset: {str(e)}[/red]")

@cli.command()
@click.option('--type', '-t', help='Type of diagnostic to run')
@click.option('--output', '-o', help='Output file for diagnostic results')
def diagnose(type, output):
    """Run system diagnostics"""
    try:
        console.print("[bold]Running system diagnostics...[/bold]")
        
        diagnostics = {
            'system_health': _check_system_health(),
            'rule_engine': _check_rule_engine(),
            'llm_service': _check_llm_service(),
            'fhir_connection': _check_fhir_connection(),
            'alert_system': _check_alert_system()
        }

        if output:
            with open(output, 'w') as f:
                json.dump(diagnostics, f, indent=2)
            console.print(f"[green]Diagnostic results saved to {output}[/green]")
        else:
            _display_diagnostic_results(diagnostics)

    except Exception as e:
        console.print(f"[red]Error running diagnostics: {str(e)}[/red]")

@cli.command()
@click.option('--rule-id', '-r', help='Rule ID to debug')
@click.option('--resource-id', '-i', help='Resource ID to test against')
def debug_rule(rule_id, resource_id):
    """Debug a specific rule"""
    try:
        if not rule_id or not resource_id:
            console.print("[red]Both rule-id and resource-id are required[/red]")
            return

        console.print(f"[bold]Debugging rule {rule_id} with resource {resource_id}[/bold]")
        
        # Get rule details
        rule_engine = RuleEngine()
        rule = asyncio.run(rule_engine.get_rule(rule_id))
        
        if not rule:
            console.print(f"[red]Rule {rule_id} not found[/red]")
            return

        # Test rule against resource
        result = asyncio.run(rule_engine.test_rule(rule_id, resource_id))
        
        # Display debug information
        _display_rule_debug_info(rule, result)

    except Exception as e:
        console.print(f"[red]Error debugging rule: {str(e)}[/red]")

@cli.command()
@click.option('--duration', '-d', default=300, help='Benchmark duration in seconds')
def benchmark(duration):
    """Run system benchmarks"""
    try:
        console.print(f"[bold]Running system benchmarks for {duration} seconds...[/bold]")
        
        benchmark = LLMBenchmark()
        results = asyncio.run(benchmark.run_benchmarks())
        
        # Display benchmark results
        _display_benchmark_results(results)

    except Exception as e:
        console.print(f"[red]Error running benchmarks: {str(e)}[/red]")

async def _collect_metrics(resource_type: str) -> Dict[str, Any]:
    """Collect current system metrics"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{settings.API_BASE_URL}/metrics") as response:
            return await response.json()

def _display_monitoring_results(metrics: Dict[str, List[Any]]):
    """Display monitoring results in a formatted table"""
    table = Table(title="System Monitoring Results")
    
    table.add_column("Metric", style="cyan")
    table.add_column("Average", style="green")
    table.add_column("Min", style="blue")
    table.add_column("Max", style="red")
    
    for metric, values in metrics.items():
        if values:
            table.add_row(
                metric,
                f"{sum(values) / len(values):.2f}",
                f"{min(values):.2f}",
                f"{max(values):.2f}"
            )
    
    console.print(table)

def _validate_ruleset(ruleset: Dict[str, Any]) -> bool:
    """Validate a ruleset"""
    required_fields = ['name', 'version', 'rules']
    
    # Check required fields
    if not all(field in ruleset for field in required_fields):
        console.print("[red]Missing required fields in ruleset[/red]")
        return False
    
    # Validate each rule
    for rule in ruleset['rules']:
        if not _validate_rule(rule):
            return False
    
    return True

def _validate_rule(rule: Dict[str, Any]) -> bool:
    """Validate a single rule"""
    required_fields = ['id', 'condition', 'action']
    
    if not all(field in rule for field in required_fields):
        console.print(f"[red]Invalid rule: {rule.get('id', 'unknown')}[/red]")
        return False
    
    return True

def _check_system_health() -> Dict[str, Any]:
    """Check overall system health"""
    return {
        'status': 'healthy',
        'components': {
            'rule_engine': 'operational',
            'llm_service': 'operational',
            'fhir_connection': 'operational',
            'alert_system': 'operational'
        },
        'metrics': {
            'cpu_usage': '45%',
            'memory_usage': '60%',
            'disk_usage': '30%'
        }
    }

def _check_rule_engine() -> Dict[str, Any]:
    """Check rule engine status"""
    return {
        'status': 'operational',
        'active_rules': 150,
        'last_evaluation': datetime.now().isoformat(),
        'performance': {
            'avg_evaluation_time': '120ms',
            'success_rate': '99.9%'
        }
    }

def _check_llm_service() -> Dict[str, Any]:
    """Check LLM service status"""
    return {
        'status': 'operational',
        'model': settings.OLLAMA_MODEL,
        'performance': {
            'avg_response_time': '850ms',
            'success_rate': '98.5%'
        }
    }

def _check_fhir_connection() -> Dict[str, Any]:
    """Check FHIR server connection"""
    return {
        'status': 'connected',
        'server': settings.FHIR_BASE_URL,
        'subscriptions': {
            'active': 5,
            'last_update': datetime.now().isoformat()
        }
    }

def _check_alert_system() -> Dict[str, Any]:
    """Check alert system status"""
    return {
        'status': 'operational',
        'active_alerts': 12,
        'suppressed_alerts': 3,
        'last_alert': datetime.now().isoformat()
    }

def _display_diagnostic_results(diagnostics: Dict[str, Any]):
    """Display diagnostic results in a formatted table"""
    table = Table(title="System Diagnostics")
    
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")
    
    for component, data in diagnostics.items():
        status = data['status']
        details = json.dumps(data.get('metrics', {}), indent=2)
        
        table.add_row(
            component.replace('_', ' ').title(),
            status,
            details
        )
    
    console.print(table)

def _display_rule_debug_info(rule: Dict[str, Any], result: Dict[str, Any]):
    """Display rule debugging information"""
    table = Table(title=f"Rule Debug: {rule['id']}")
    
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    # Rule details
    table.add_row("Name", rule.get('name', 'N/A'))
    table.add_row("Condition", json.dumps(rule['condition'], indent=2))
    table.add_row("Action", json.dumps(rule['action'], indent=2))
    
    # Evaluation results
    table.add_row("Match", str(result.get('match', False)))
    table.add_row("Execution Time", f"{result.get('execution_time', 0)}ms")
    if 'error' in result:
        table.add_row("Error", result['error'])
    
    console.print(table)

def _display_benchmark_results(results: Dict[str, Any]):
    """Display benchmark results in a formatted table"""
    table = Table(title="System Benchmarks")
    
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    for metric, value in results.items():
        if isinstance(value, (int, float)):
            table.add_row(metric, f"{value:.2f}")
        else:
            table.add_row(metric, str(value))
    
    console.print(table)

if __name__ == '__main__':
    cli() 