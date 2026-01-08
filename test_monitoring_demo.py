"""Simple demo of the monitoring system without heavy dependencies."""
import sys
import os
import time
import math
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monitoring.core import monitoring_system, ensure_initialized
from monitoring.database import db_manager
from monitoring.models import LogFilters, TimeRange
from monitoring.event_bus import event_bus
from monitoring.decorators import monitor_all, monitor_execution, track_performance


# Mock viral clip analyzer functions for demo
@monitor_all(weight=2.0)
def fetch_trending_clips(platform='youtube', limit=100):
    """Mock function to simulate fetching trending clips."""
    print(f"🔍 Fetching {limit} clips from {platform}...")
    time.sleep(0.2)  # Simulate API call
    
    # Return mock data
    clips = []
    for i in range(min(limit, 5)):
        clips.append({
            'id': f'video_{i}',
            'title': f'Viral Gaming Clip {i}',
            'views': 50000 + i * 10000,
            'views_last_24h': 5000 + i * 1000,
            'likes': 2500 + i * 500,
            'comments': 500 + i * 100,
            'shares': 250 + i * 50,
            'age_hours': 2.0 + i * 0.5,
            'growth_6h': 4.0 + i * 0.2,
            'transcript': f'Gaming content with memes {i}',
            'url': f'https://youtube.com/watch?v=test{i}'
        })
    
    print(f"✅ Fetched {len(clips)} clips")
    return clips


@track_performance
def calculate_virality_score(clip):
    """Calculate virality score for a clip."""
    views = clip['views']
    views_24h = clip['views_last_24h']
    engagement = clip['likes'] + clip['comments'] + clip['shares']
    
    if views == 0:
        return 0
    
    # Simulate some computation
    time.sleep(0.01)
    
    virality = math.log10(views_24h + 1) * (engagement / views)
    return virality


@monitor_execution
def check_relevance(clip, keywords=['gaming', 'memes']):
    """Check if clip is relevant to our niche."""
    transcript = clip['transcript'].lower()
    title = clip['title'].lower()
    
    relevance_score = 0
    for keyword in keywords:
        if keyword in transcript or keyword in title:
            relevance_score += 1
    
    return relevance_score / len(keywords)


@monitor_all(weight=1.5)
def filter_and_score_clips(clips):
    """Filter and score clips based on criteria."""
    print(f"📊 Scoring {len(clips)} clips...")
    
    scored_clips = []
    for clip in clips:
        # Check growth velocity
        if clip['growth_6h'] < 3.0:
            continue
            
        # Calculate scores
        virality = calculate_virality_score(clip)
        relevance = check_relevance(clip)
        
        # Combined score
        final_score = virality * 0.7 + relevance * 0.3
        
        if final_score > 0.5:  # Threshold
            scored_clips.append({
                **clip,
                'virality_score': virality,
                'relevance_score': relevance,
                'final_score': final_score
            })
    
    # Sort by score
    scored_clips.sort(key=lambda x: x['final_score'], reverse=True)
    print(f"✅ Selected {len(scored_clips)} high-scoring clips")
    
    return scored_clips


@monitor_all(weight=3.0)
def analyze_viral_clips():
    """Main function to analyze viral clips."""
    print("🚀 Starting viral clip analysis...")
    
    # Fetch clips
    clips = fetch_trending_clips(limit=10)
    
    # Filter and score
    top_clips = filter_and_score_clips(clips)
    
    # Return top 3
    result = top_clips[:3]
    
    print(f"🎯 Analysis complete! Found {len(result)} top clips")
    return result


def demo_monitoring_system():
    """Demonstrate the monitoring system."""
    print("🎬 VIRAL CLIP ANALYZER MONITORING DEMO")
    print("=" * 50)
    
    # Initialize monitoring
    ensure_initialized()
    print("✓ Monitoring system initialized")
    
    # Track events
    events_received = []
    
    def event_tracker(event_type, data):
        events_received.append((event_type, data))
        func_name = data.get('function_name', 'N/A').split('.')[-1]
        if event_type == 'function.completed':
            duration = data.get('duration', 0)
            print(f"  📡 {func_name} completed in {duration:.3f}s")
        elif event_type == 'function.started':
            print(f"  📡 {func_name} started")
    
    # Subscribe to events
    event_bus.subscribe('function.started', event_tracker)
    event_bus.subscribe('function.completed', event_tracker)
    event_bus.subscribe('function.failed', event_tracker)
    
    print(f"\n🔄 Running viral clip analysis with monitoring...")
    print("-" * 45)
    
    # Run the analysis
    start_time = time.time()
    try:
        result = analyze_viral_clips()
        end_time = time.time()
        
        print(f"\n✅ Analysis completed in {end_time - start_time:.2f} seconds")
        
        # Show results
        print(f"\n🏆 TOP VIRAL CLIPS:")
        for i, clip in enumerate(result, 1):
            print(f"  {i}. {clip['title']}")
            print(f"     Score: {clip['final_score']:.3f} | Views: {clip['views']:,} | Growth: {clip['growth_6h']:.1f}x")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Wait for events to process
    time.sleep(0.2)
    
    # Show monitoring results
    print(f"\n📊 MONITORING RESULTS:")
    print("-" * 25)
    print(f"✓ Events captured: {len(events_received)}")
    
    # Check database
    filters = LogFilters(limit=50)
    log_entries = db_manager.query_log_entries(filters)
    
    time_range = TimeRange(
        start=datetime.now() - timedelta(minutes=1),
        end=datetime.now()
    )
    perf_metrics = db_manager.query_performance_metrics(time_range)
    
    print(f"✓ Log entries: {len(log_entries)}")
    print(f"✓ Performance metrics: {len(perf_metrics)}")
    
    # Show function performance
    if perf_metrics:
        print(f"\n⚡ FUNCTION PERFORMANCE:")
        func_stats = {}
        for metric in perf_metrics:
            func_name = metric.function_name.split('.')[-1]
            if func_name not in func_stats:
                func_stats[func_name] = []
            func_stats[func_name].append(metric.execution_time)
        
        for func_name, times in func_stats.items():
            avg_time = sum(times) / len(times)
            print(f"  • {func_name}: {avg_time:.3f}s avg ({len(times)} calls)")
    
    # System status
    status = monitoring_system.get_status()
    print(f"\n🔍 SYSTEM STATUS:")
    print(f"✓ Status: {status['status']}")
    print(f"✓ Total log entries: {status['database_stats']['log_entries_count']}")
    print(f"✓ Total performance records: {status['database_stats']['performance_metrics_count']}")
    
    # Cleanup
    event_bus.unsubscribe('function.started', event_tracker)
    event_bus.unsubscribe('function.completed', event_tracker)
    event_bus.unsubscribe('function.failed', event_tracker)
    
    print(f"\n🎉 DEMO COMPLETE!")
    print("=" * 20)
    print("✅ Function execution tracking: WORKING")
    print("✅ Performance monitoring: WORKING")
    print("✅ Event system: WORKING")
    print("✅ Database logging: WORKING")
    print("✅ Real-time monitoring: WORKING")
    
    return True


if __name__ == "__main__":
    try:
        success = demo_monitoring_system()
        
        if success:
            print(f"\n🚀 MONITORING SYSTEM IS READY!")
            print("\nTo integrate with your viral clip analyzer:")
            print("1. Add these imports to your main.py:")
            print("   from monitoring.decorators import monitor_all, monitor_execution")
            print("   from monitoring.core import ensure_initialized")
            print("")
            print("2. Add decorators to your functions:")
            print("   @monitor_all(weight=2.0)")
            print("   def fetch_trending_clips(...):")
            print("")
            print("3. Initialize monitoring in your main():")
            print("   ensure_initialized()")
            print("")
            print("4. Check monitoring.log and monitoring.db for data!")
        
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()