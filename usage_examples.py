"""
Usage Examples for Viral Clip Analyzer with Monitoring
Demonstrates all key features and data access patterns
"""
import json
from datetime import datetime, timedelta
from data_access import ViralClipDataAccess, create_sample_data
from monitoring.core import ensure_initialized, monitoring_system
from monitoring.database import db_manager
from monitoring.models import LogFilters, TimeRange


def demo_data_filtering():
    """Demonstrate various data filtering options"""
    print("🔍 DATA FILTERING EXAMPLES")
    print("=" * 40)
    
    # Initialize with sample data
    data_access = create_sample_data()
    
    print("1. Filter by Score Range:")
    high_score_clips = data_access.filter_clips(min_score=18, max_score=25)
    for clip in high_score_clips:
        print(f"   • {clip['title']} - Score: {clip['scores']['final_score']}")
    
    print(f"\n2. Filter by Platform:")
    platforms = ['youtube', 'tiktok', 'instagram']
    for platform in platforms:
        clips = data_access.filter_clips(platform=platform)
        print(f"   • {platform.title()}: {len(clips)} clips")
    
    print(f"\n3. Filter by Views:")
    high_view_clips = data_access.filter_clips(min_views=200000)
    for clip in high_view_clips:
        print(f"   • {clip['title']} - Views: {clip['views']:,}")
    
    print(f"\n4. Filter by Growth Rate:")
    trending_clips = data_access.filter_clips(min_growth=3.5)
    for clip in trending_clips:
        print(f"   • {clip['title']} - Growth: {clip['growth_6h']:.1f}x")
    
    print(f"\n5. Search by Keywords:")
    gaming_clips = data_access.filter_clips(keywords=['gaming'])
    for clip in gaming_clips:
        print(f"   • {clip['title']} - Platform: {clip['platform']}")
    
    print(f"\n6. Complex Filter (High score + Recent + Gaming):")
    complex_filter = data_access.filter_clips(
        min_score=15,
        max_age_hours=24,
        keywords=['gaming'],
        limit=5
    )
    print(f"   Found {len(complex_filter)} clips matching all criteria")


def demo_json_data_structure():
    """Show the JSON data structure and key-value format"""
    print("\n📋 JSON DATA STRUCTURE")
    print("=" * 30)
    
    data_access = ViralClipDataAccess()
    
    # Show the complete data structure
    sample_structure = {
        "clips": [
            {
                "id": "unique_video_id",
                "title": "Video Title",
                "platform": "youtube|tiktok|instagram",
                "views": 150000,
                "views_last_24h": 25000,
                "likes": 8500,
                "comments": 1200,
                "shares": 450,
                "age_hours": 6.5,
                "growth_6h": 4.2,
                "transcript": "Video content description",
                "thumbnail_url": "https://...",
                "url": "https://...",
                "scores": {
                    "virality": 0.85,
                    "relevance": 0.92,
                    "final_score": 18.7
                },
                "metadata": {
                    "processed_at": "2024-01-08T10:30:00Z",
                    "niche_match": ["gaming", "funny"],
                    "reactability": 0.8
                }
            }
        ],
        "summary": {
            "total_clips": 150,
            "filtered_clips": 12,
            "processing_time": 45.2,
            "timestamp": "2024-01-08T10:30:00Z"
        },
        "metadata": {
            "version": "1.0",
            "created_at": "2024-01-08T10:00:00Z",
            "last_updated": "2024-01-08T10:30:00Z"
        }
    }
    
    print("Key-Value Structure:")
    print(json.dumps(sample_structure, indent=2)[:500] + "...")
    
    print(f"\nAvailable Filter Keys:")
    filter_keys = [
        "platform", "min_views", "max_views", "min_score", "max_score",
        "min_growth", "max_age_hours", "keywords", "limit"
    ]
    for key in filter_keys:
        print(f"   • {key}")


def demo_monitoring_integration():
    """Demonstrate monitoring system integration"""
    print("\n📊 MONITORING INTEGRATION")
    print("=" * 35)
    
    # Initialize monitoring
    ensure_initialized()
    
    # Show system status
    status = monitoring_system.get_status()
    print(f"Monitoring Status: {status['status']}")
    print(f"Database Entries: {status['database_stats']['log_entries_count']}")
    
    # Get recent performance data
    data_access = ViralClipDataAccess()
    perf_summary = data_access.get_performance_summary()
    
    if "error" not in perf_summary:
        print(f"\nPerformance Summary:")
        summary = perf_summary['summary']
        print(f"   • Total executions: {summary['total_executions']}")
        print(f"   • Total time: {summary['total_time']}s")
        print(f"   • Average time: {summary['avg_execution_time']}s")
        print(f"   • Average memory: {summary['avg_memory_mb']}MB")
        
        if 'function_performance' in perf_summary:
            print(f"\nFunction Performance:")
            for func, stats in perf_summary['function_performance'].items():
                print(f"   • {func}: {stats['avg_time']:.3f}s avg ({stats['calls']} calls)")


def demo_export_options():
    """Demonstrate data export capabilities"""
    print("\n💾 EXPORT OPTIONS")
    print("=" * 20)
    
    data_access = create_sample_data()
    
    # Export all data
    success = data_access.export_clips("all_clips.json", format="json")
    print(f"1. Export all clips (JSON): {'✅' if success else '❌'}")
    
    # Export filtered data
    success = data_access.export_clips(
        "high_score_clips.json", 
        format="json",
        filters={"min_score": 18}
    )
    print(f"2. Export high-score clips: {'✅' if success else '❌'}")
    
    # Export by platform
    success = data_access.export_clips(
        "youtube_clips.json",
        format="json", 
        filters={"platform": "youtube"}
    )
    print(f"3. Export YouTube clips: {'✅' if success else '❌'}")
    
    print(f"\nExported Files:")
    import os
    export_files = ["all_clips.json", "high_score_clips.json", "youtube_clips.json"]
    for file in export_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   • {file} ({size:,} bytes)")


def demo_real_world_usage():
    """Show real-world usage patterns"""
    print("\n🚀 REAL-WORLD USAGE PATTERNS")
    print("=" * 40)
    
    data_access = create_sample_data()
    
    print("1. Find clips for reaction video:")
    reaction_clips = data_access.filter_clips(
        min_score=15,           # High viral potential
        max_age_hours=48,       # Recent content
        min_growth=3.0,         # Trending
        keywords=['gaming'],    # Your niche
        limit=5                 # Top 5 only
    )
    print(f"   Found {len(reaction_clips)} suitable clips")
    
    print(f"\n2. Platform comparison:")
    platforms = {}
    for platform in ['youtube', 'tiktok', 'instagram']:
        clips = data_access.filter_clips(platform=platform, min_score=15)
        avg_score = sum(c['scores']['final_score'] for c in clips) / len(clips) if clips else 0
        platforms[platform] = {'count': len(clips), 'avg_score': avg_score}
    
    for platform, stats in platforms.items():
        print(f"   • {platform.title()}: {stats['count']} clips, avg score: {stats['avg_score']:.1f}")
    
    print(f"\n3. Trending analysis:")
    all_clips = data_access.get_all_clips()
    trending_count = len([c for c in all_clips if c['growth_6h'] >= 3.0])
    high_score_count = len([c for c in all_clips if c['scores']['final_score'] >= 18])
    
    print(f"   • Trending clips (>3x growth): {trending_count}")
    print(f"   • High-score clips (>18): {high_score_count}")
    print(f"   • Overlap (trending + high-score): {len(data_access.filter_clips(min_growth=3.0, min_score=18))}")


def demo_api_usage():
    """Show how to use the data access API"""
    print("\n🔧 API USAGE EXAMPLES")
    print("=" * 25)
    
    print("Python Code Examples:")
    
    code_examples = [
        ("Initialize data access", "data_access = ViralClipDataAccess()"),
        ("Get top clips", "top_clips = data_access.get_top_clips(limit=10)"),
        ("Filter by platform", "youtube_clips = data_access.get_clips_by_platform('youtube')"),
        ("Search by keywords", "gaming_clips = data_access.search_clips(['gaming', 'funny'])"),
        ("Get trending clips", "trending = data_access.get_trending_clips(growth_threshold=3.0)"),
        ("Complex filtering", "clips = data_access.filter_clips(min_score=15, platform='youtube', limit=5)"),
        ("Export data", "data_access.export_clips('export.json', filters={'min_score': 18})"),
        ("Get summary", "summary = data_access.get_summary()"),
    ]
    
    for description, code in code_examples:
        print(f"\n   {description}:")
        print(f"   {code}")


if __name__ == "__main__":
    print("🎬 VIRAL CLIP ANALYZER - COMPLETE USAGE GUIDE")
    print("=" * 55)
    
    try:
        # Run all demos
        demo_data_filtering()
        demo_json_data_structure()
        demo_monitoring_integration()
        demo_export_options()
        demo_real_world_usage()
        demo_api_usage()
        
        print(f"\n🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 40)
        print("✅ Data filtering: Working")
        print("✅ JSON structure: Defined")
        print("✅ Monitoring integration: Active")
        print("✅ Export capabilities: Ready")
        print("✅ Real-world patterns: Demonstrated")
        print("✅ API usage: Documented")
        
        print(f"\n📁 Files created:")
        import os
        files = [
            "viral_clips_data.json", "sample_export.json", 
            "all_clips.json", "high_score_clips.json", "youtube_clips.json"
        ]
        for file in files:
            if os.path.exists(file):
                print(f"   • {file}")
        
        print(f"\n🚀 Ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()