"""
MLOps Monitoring Example
Demonstrates monitoring, metrics collection, and API gateway usage
"""

import sys
from pathlib import Path
import logging
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mlops.monitoring import MetricsCollector, PerformanceMonitor
from mlops.api_gateway import APIGateway, validate_payload, log_request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_api_gateway():
    """Example: Basic API Gateway with rate limiting."""
    logger.info("=" * 60)
    logger.info("Example 1: API Gateway with Rate Limiting")
    logger.info("=" * 60)
    
    # Create gateway
    gateway = APIGateway(rate_limit=10, rate_period=60)
    
    # Register tokens
    gateway.register_token("sk-demo-token-123")
    gateway.register_token("sk-demo-token-456")
    
    # Add middleware
    gateway.add_middleware(log_request)
    gateway.add_middleware(validate_payload)
    
    # Register route handlers
    def create_task(data):
        return {
            "task_id": "task-001",
            "status": "created",
            "name": data.get("name", "Unnamed")
        }
    
    def get_task(data):
        return {
            "task_id": "task-001",
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
    
    gateway.register_route("/api/tasks", create_task, methods=["POST"])
    gateway.register_route("/api/tasks/get", get_task, methods=["GET"])
    
    # Test requests
    print("\n📨 Test 1: Valid POST request")
    response = gateway.handle_request(
        method="POST",
        path="/api/tasks",
        data={"name": "Deploy model v2"},
        token="sk-demo-token-123",
        client_id="client-1"
    )
    print(f"Response: {response}")
    print(f"Remaining requests: {response.get('remaining_requests', 'N/A')}/10")
    
    print("\n📨 Test 2: Valid GET request")
    response = gateway.handle_request(
        method="GET",
        path="/api/tasks/get",
        token="sk-demo-token-123",
        client_id="client-1"
    )
    print(f"Response: {response}")
    
    print("\n📨 Test 3: Unauthorized request (no token)")
    response = gateway.handle_request(
        method="GET",
        path="/api/tasks/get",
        token=None,
        client_id="client-1"
    )
    print(f"Response: {response}")
    
    print("\n📨 Test 4: Invalid route")
    response = gateway.handle_request(
        method="GET",
        path="/api/invalid",
        token="sk-demo-token-123",
        client_id="client-1"
    )
    print(f"Response: {response}")
    
    # Rate limit test
    print("\n📊 Rate Limiting Test (10 requests/minute)")
    client_2_responses = []
    for i in range(12):
        response = gateway.handle_request(
            method="GET",
            path="/api/tasks/get",
            token="sk-demo-token-123",
            client_id="client-2"
        )
        status = response.get("status")
        client_2_responses.append(status)
        print(f"Request {i+1}: Status {status} - Remaining: {response.get('remaining_requests', 0)}/10")
    
    # Check rate limiting worked
    rate_limited = any(status == 429 for status in client_2_responses)
    print(f"\n✅ Rate limiting enforced: {rate_limited}")
    
    # Show metrics
    print(f"\n📈 Gateway Metrics:")
    metrics = gateway.get_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")


def example_metrics_collection():
    """Example: Collect and analyze performance metrics."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: Metrics Collection & Analysis")
    logger.info("=" * 60)
    
    # Create collectors
    metrics = MetricsCollector()
    monitor = PerformanceMonitor()
    
    print("\n📊 Simulating model inference requests...")
    
    # Simulate 20 inference requests
    for i in range(20):
        start_time = time.time()
        
        # Simulate variable latency (50-500ms)
        import random
        latency = random.uniform(0.05, 0.5)
        time.sleep(latency)
        
        # Record metrics
        metrics.record_latency(latency)
        metrics.record_memory_usage(random.uniform(2.0, 6.0))  # GB
        metrics.record_accuracy(random.uniform(0.85, 0.99))  # 85-99% accuracy
        
        print(f"Request {i+1}: {latency*1000:.2f}ms latency")
    
    # Get statistics
    print("\n📈 Metrics Summary:")
    stats = metrics.get_statistics()
    for metric, values in stats.items():
        print(f"\n{metric}:")
        for stat_name, stat_value in values.items():
            if isinstance(stat_value, float):
                print(f"  {stat_name}: {stat_value:.4f}")
            else:
                print(f"  {stat_name}: {stat_value}")
    
    # Check thresholds
    print("\n⚠️  Threshold Checks:")
    latencies = metrics.latencies
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        print(f"  Average Latency: {avg_latency*1000:.2f}ms (threshold: 500ms)")
        print(f"  Status: {'✅ OK' if avg_latency < 0.5 else '❌ EXCEEDED'}")
    
    memory = metrics.memory_usage
    if memory:
        avg_memory = sum(memory) / len(memory)
        print(f"  Average Memory: {avg_memory:.2f}GB (threshold: 8GB)")
        print(f"  Status: {'✅ OK' if avg_memory < 8.0 else '❌ EXCEEDED'}")
    
    accuracy = metrics.accuracy
    if accuracy:
        avg_accuracy = sum(accuracy) / len(accuracy)
        print(f"  Average Accuracy: {avg_accuracy:.4f} (threshold: 0.80)")
        print(f"  Status: {'✅ OK' if avg_accuracy > 0.80 else '❌ BELOW'}")


def example_alert_management():
    """Example: Alert management and notifications."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: Alert Management")
    logger.info("=" * 60)
    
    monitor = PerformanceMonitor()
    
    print("\n🚨 Simulating alerts...")
    
    # Simulate high latency alert
    monitor.add_alert(
        alert_type="performance",
        severity="high",
        message="Model inference latency exceeded 500ms",
        metrics={"latency_ms": 650}
    )
    
    # Simulate memory alert
    monitor.add_alert(
        alert_type="resource",
        severity="critical",
        message="Memory usage at 8.5GB (exceeds 8GB threshold)",
        metrics={"memory_gb": 8.5}
    )
    
    # Simulate accuracy alert
    monitor.add_alert(
        alert_type="model",
        severity="medium",
        message="Model accuracy dropped below threshold",
        metrics={"accuracy": 0.75}
    )
    
    # Display alerts
    alerts = monitor.get_alerts()
    print(f"\n📋 Active Alerts ({len(alerts)}):")
    for i, alert in enumerate(alerts, 1):
        print(f"\n  {i}. [{alert['severity'].upper()}] {alert['alert_type']}")
        print(f"     Message: {alert['message']}")
        print(f"     Time: {alert['timestamp']}")
        print(f"     Metrics: {alert.get('metrics', {})}")
    
    # Clear critical alerts
    print("\n🔧 Clearing critical alerts...")
    monitor.clear_alerts_by_severity("critical")
    remaining = monitor.get_alerts()
    print(f"Remaining alerts: {len(remaining)}")


def example_prometheus_export():
    """Example: Export metrics in Prometheus format."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 4: Prometheus Metrics Export")
    logger.info("=" * 60)
    
    metrics = MetricsCollector()
    
    # Simulate some data
    import random
    for _ in range(10):
        metrics.record_latency(random.uniform(0.05, 0.3))
        metrics.record_memory_usage(random.uniform(2.0, 5.0))
        metrics.record_accuracy(random.uniform(0.90, 0.98))
    
    print("\n📊 Prometheus Format Metrics:")
    print("-" * 60)
    
    # Export in Prometheus format
    stats = metrics.get_statistics()
    
    print("# HELP eacp_latency_seconds Model inference latency")
    print("# TYPE eacp_latency_seconds gauge")
    if "latency" in stats:
        avg_lat = stats["latency"].get("average", 0)
        print(f'eacp_latency_seconds{{quantile="avg"}} {avg_lat}')
    
    print("\n# HELP eacp_memory_bytes Memory usage")
    print("# TYPE eacp_memory_bytes gauge")
    if "memory" in stats:
        avg_mem = stats["memory"].get("average", 0) * 1e9  # Convert GB to bytes
        print(f'eacp_memory_bytes{{instance="default"}} {avg_mem:.0f}')
    
    print("\n# HELP eacp_accuracy Model accuracy")
    print("# TYPE eacp_accuracy gauge")
    if "accuracy" in stats:
        avg_acc = stats["accuracy"].get("average", 0)
        print(f'eacp_accuracy{{model="default"}} {avg_acc}')
    
    print("-" * 60)


if __name__ == "__main__":
    print("\n" + "🎯 EACP MLOps Monitoring Examples".center(60, "="))
    
    try:
        example_api_gateway()
        example_metrics_collection()
        example_alert_management()
        example_prometheus_export()
        
        print("\n" + "✅ All examples completed successfully".center(60, "=") + "\n")
    
    except Exception as e:
        logger.error(f"Example error: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}\n")
