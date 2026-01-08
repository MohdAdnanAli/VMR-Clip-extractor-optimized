"""
Data Access Layer for Viral Movements Analyzer
Provides key-value JSON format for filtering and accessing viral movements data
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import sqlite3

from monitoring.database import db_manager
from monitoring.models import LogFilters, TimeRange, PerformanceMetrics


@dataclass
class MovementData:
    """Structured movement data model"""
    id: str
    title: str
    platform: str
    views: int
    views_last_24h: int
    likes: int
    comments: int
    shares: int
    age_hours: float
    growth_6h: float
    transcript: str
    thumbnail_url: str
    url: str
    scores: Dict[str, float]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ViralMovementsDataAccess:
    """
    Data access layer for viral movements data with JSON key-value filtering
    """
    
    def __init__(self, data_file: str = "viral_movements_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file or create empty structure"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Return empty structure
        return {
            "movements": [],
            "summary": {
                "total_movements": 0,
                "filtered_movements": 0,
                "processing_time": 0.0,
                "timestamp": datetime.now().isoformat()
            },
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def _save_data(self) -> None:
        """Save data to JSON file"""
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def add_movements(self, movements: List[Dict[str, Any]]) -> None:
        """Add new movements to the data store"""
        for movement in movements:
            # Ensure required structure
            movement_data = {
                "id": movement.get("id", ""),
                "title": movement.get("title", ""),
                "platform": movement.get("platform", "unknown"),
                "views": movement.get("views", 0),
                "views_last_24h": movement.get("views_last_24h", 0),
                "likes": movement.get("likes", 0),
                "comments": movement.get("comments", 0),
                "shares": movement.get("shares", 0),
                "age_hours": movement.get("age_hours", 0.0),
                "growth_6h": movement.get("growth_6h", 0.0),
                "transcript": movement.get("transcript", ""),
                "thumbnail_url": movement.get("thumbnail_url", ""),
                "url": movement.get("url", ""),
                "scores": movement.get("scores", {}),
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "niche_match": movement.get("niche_match", []),
                    "reactability": movement.get("reactability", 0.0),
                    **movement.get("metadata", {})
                }
            }
            
            # Remove existing movement with same ID
            self.data["movements"] = [c for c in self.data["movements"] if c["id"] != movement_data["id"]]
            
            # Add new movement
            self.data["movements"].append(movement_data)
        
        # Update summary
        self.data["summary"]["total_movements"] = len(self.data["movements"])
        self.data["summary"]["timestamp"] = datetime.now().isoformat()
        
        self._save_data()
    
    def get_all_movements(self) -> List[Dict[str, Any]]:
        """Get all movements"""
        return self.data["movements"]
    
    def filter_movements(self, **filters) -> List[Dict[str, Any]]:
        """
        Filter movements using key-value pairs
        
        Available filters:
        - platform: str (youtube, tiktok, instagram)
        - min_views: int
        - max_views: int
        - min_score: float
        - max_score: float
        - min_growth: float
        - max_age_hours: float
        - keywords: List[str] (search in title/transcript)
        - limit: int
        """
        movements = self.data["movements"].copy()
        
        # Platform filter
        if "platform" in filters:
            movements = [c for c in movements if c["platform"] == filters["platform"]]
        
        # Views filters
        if "min_views" in filters:
            movements = [c for c in movements if c["views"] >= filters["min_views"]]
        if "max_views" in filters:
            movements = [c for c in movements if c["views"] <= filters["max_views"]]
        
        # Score filters
        if "min_score" in filters:
            movements = [c for c in movements if c["scores"].get("final_score", 0) >= filters["min_score"]]
        if "max_score" in filters:
            movements = [c for c in movements if c["scores"].get("final_score", 0) <= filters["max_score"]]
        
        # Growth filter
        if "min_growth" in filters:
            movements = [c for c in movements if c["growth_6h"] >= filters["min_growth"]]
        
        # Age filter
        if "max_age_hours" in filters:
            movements = [c for c in movements if c["age_hours"] <= filters["max_age_hours"]]
        
        # Keyword search
        if "keywords" in filters:
            keywords = [k.lower() for k in filters["keywords"]]
            filtered_movements = []
            for movement in movements:
                text = (movement["title"] + " " + movement["transcript"]).lower()
                if any(keyword in text for keyword in keywords):
                    filtered_movements.append(movement)
            movements = filtered_movements
        
        # Sort by score (highest first)
        movements.sort(key=lambda x: x["scores"].get("final_score", 0), reverse=True)
        
        # Limit results
        if "limit" in filters:
            movements = movements[:filters["limit"]]
        
        return movements
    
    def get_movements_by_score(self, min_score: float = 0, max_score: float = 100, limit: int = None) -> List[Dict[str, Any]]:
        """Get movements filtered by score range"""
        return self.filter_movements(min_score=min_score, max_score=max_score, limit=limit)
    
    def get_movements_by_platform(self, platform: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get movements from specific platform"""
        return self.filter_movements(platform=platform, limit=limit)
    
    def get_trending_movements(self, growth_threshold: float = 3.0, limit: int = None) -> List[Dict[str, Any]]:
        """Get movements with high growth rate"""
        return self.filter_movements(min_growth=growth_threshold, limit=limit)
    
    def get_movements_by_timeframe(self, hours: int = 24, limit: int = None) -> List[Dict[str, Any]]:
        """Get movements within specified age"""
        return self.filter_movements(max_age_hours=hours, limit=limit)
    
    def search_movements(self, keywords: List[str], limit: int = None) -> List[Dict[str, Any]]:
        """Search movements by keywords in title/transcript"""
        return self.filter_movements(keywords=keywords, limit=limit)
    
    def get_top_movements(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top movements by final score"""
        return self.filter_movements(limit=limit)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get data summary"""
        movements = self.data["movements"]
        
        if not movements:
            return self.data["summary"]
        
        # Calculate statistics
        scores = [c["scores"].get("final_score", 0) for c in movements]
        views = [c["views"] for c in movements]
        platforms = {}
        
        for movement in movements:
            platform = movement["platform"]
            platforms[platform] = platforms.get(platform, 0) + 1
        
        summary = {
            **self.data["summary"],
            "statistics": {
                "total_movements": len(movements),
                "avg_score": sum(scores) / len(scores) if scores else 0,
                "max_score": max(scores) if scores else 0,
                "min_score": min(scores) if scores else 0,
                "avg_views": sum(views) / len(views) if views else 0,
                "max_views": max(views) if views else 0,
                "platforms": platforms,
                "high_score_movements": len([s for s in scores if s >= 15]),
                "trending_movements": len([c for c in movements if c["growth_6h"] >= 3.0])
            }
        }
        
        return summary
    
    def export_movements(self, filename: str, format: str = "json", filters: Dict = None) -> bool:
        """Export movements to file"""
        try:
            movements = self.filter_movements(**(filters or {}))
            
            if format.lower() == "json":
                export_data = {
                    "movements": movements,
                    "summary": self.get_summary(),
                    "exported_at": datetime.now().isoformat(),
                    "filters_applied": filters or {}
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == "csv":
                import pandas as pd
                
                # Flatten movement data for CSV
                flattened_movements = []
                for movement in movements:
                    flat_movement = {
                        **movement,
                        "final_score": movement["scores"].get("final_score", 0),
                        "virality_score": movement["scores"].get("virality", 0),
                        "relevance_score": movement["scores"].get("relevance", 0),
                        "processed_at": movement["metadata"].get("processed_at", ""),
                        "reactability": movement["metadata"].get("reactability", 0)
                    }
                    # Remove nested objects
                    flat_movement.pop("scores", None)
                    flat_movement.pop("metadata", None)
                    flattened_movements.append(flat_movement)
                
                df = pd.DataFrame(flattened_movements)
                df.to_csv(filename, index=False)
            
            return True
            
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics from monitoring system"""
        try:
            # Get recent performance data
            time_range = TimeRange(
                start=datetime.now() - timedelta(hours=24),
                end=datetime.now()
            )
            
            metrics = db_manager.query_performance_metrics(time_range)
            
            if not metrics:
                return {"error": "No performance data available"}
            
            # Calculate summary statistics
            total_time = sum(m.execution_time for m in metrics)
            avg_time = total_time / len(metrics)
            avg_memory = sum(m.memory_peak for m in metrics) / len(metrics) / 1024 / 1024  # MB
            
            function_stats = {}
            for metric in metrics:
                func_name = metric.function_name.split('.')[-1]
                if func_name not in function_stats:
                    function_stats[func_name] = {
                        "calls": 0,
                        "total_time": 0,
                        "avg_time": 0,
                        "max_time": 0
                    }
                
                function_stats[func_name]["calls"] += 1
                function_stats[func_name]["total_time"] += metric.execution_time
                function_stats[func_name]["max_time"] = max(
                    function_stats[func_name]["max_time"], 
                    metric.execution_time
                )
            
            # Calculate averages
            for func_name in function_stats:
                stats = function_stats[func_name]
                stats["avg_time"] = stats["total_time"] / stats["calls"]
            
            return {
                "summary": {
                    "total_executions": len(metrics),
                    "total_time": round(total_time, 3),
                    "avg_execution_time": round(avg_time, 3),
                    "avg_memory_mb": round(avg_memory, 1),
                    "time_range": {
                        "start": time_range.start.isoformat(),
                        "end": time_range.end.isoformat()
                    }
                },
                "function_performance": function_stats
            }
            
        except Exception as e:
            return {"error": f"Failed to get performance data: {str(e)}"}
    
    def export_clips(self, filename: str, format: str = "json", filters: Dict = None) -> bool:
        """Export clips to file"""
        try:
            clips = self.filter_clips(**(filters or {}))
            
            if format.lower() == "json":
                export_data = {
                    "clips": clips,
                    "summary": self.get_summary(),
                    "exported_at": datetime.now().isoformat(),
                    "filters_applied": filters or {}
                }
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == "csv":
                import pandas as pd
                
                # Flatten clip data for CSV
                flattened_clips = []
                for clip in clips:
                    flat_clip = {
                        **clip,
                        "final_score": clip["scores"].get("final_score", 0),
                        "virality_score": clip["scores"].get("virality", 0),
                        "relevance_score": clip["scores"].get("relevance", 0),
                        "processed_at": clip["metadata"].get("processed_at", ""),
                        "reactability": clip["metadata"].get("reactability", 0)
                    }
                    # Remove nested objects
                    flat_clip.pop("scores", None)
                    flat_clip.pop("metadata", None)
                    flattened_clips.append(flat_clip)
                
                df = pd.DataFrame(flattened_clips)
                df.to_csv(filename, index=False)
            
            return True
            
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def clear_data(self) -> None:
        """Clear all movement data"""
        self.data = {
            "movements": [],
            "summary": {
                "total_movements": 0,
                "filtered_movements": 0,
                "processing_time": 0.0,
                "timestamp": datetime.now().isoformat()
            },
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }
        self._save_data()


# Example usage and demo data
def create_sample_data():
    """Create sample viral movements data for testing"""
    data_access = ViralMovementsDataAccess()
    
    sample_movements = [
        {
            "id": "yt_gaming_001",
            "title": "INSANE Gaming Moment - You Won't Believe This!",
            "platform": "youtube",
            "views": 250000,
            "views_last_24h": 45000,
            "likes": 12500,
            "comments": 2800,
            "shares": 1200,
            "age_hours": 8.5,
            "growth_6h": 4.2,
            "transcript": "Epic gaming moment with incredible skill and funny reactions",
            "thumbnail_url": "https://img.youtube.com/vi/gaming_001/maxresdefault.jpg",
            "url": "https://youtube.com/watch?v=gaming_001",
            "scores": {
                "virality": 0.87,
                "relevance": 0.94,
                "final_score": 22.3
            },
            "niche_match": ["gaming", "funny"],
            "reactability": 0.9
        },
        {
            "id": "tt_meme_002",
            "title": "When you realize it's Monday (sad face)",
            "platform": "tiktok",
            "views": 180000,
            "views_last_24h": 35000,
            "likes": 8900,
            "comments": 1500,
            "shares": 2100,
            "age_hours": 12.0,
            "growth_6h": 3.8,
            "transcript": "Relatable Monday mood meme with perfect timing",
            "thumbnail_url": "https://tiktok.com/thumb/meme_002.jpg",
            "url": "https://tiktok.com/@user/video/meme_002",
            "scores": {
                "virality": 0.82,
                "relevance": 0.88,
                "final_score": 19.7
            },
            "niche_match": ["memes", "relatable"],
            "reactability": 0.85
        },
        {
            "id": "ig_gaming_003",
            "title": "Pro Gamer Destroys Noobs",
            "platform": "instagram",
            "views": 95000,
            "views_last_24h": 18000,
            "likes": 4200,
            "comments": 890,
            "shares": 320,
            "age_hours": 18.5,
            "growth_6h": 2.9,
            "transcript": "Professional gaming highlights with amazing plays",
            "thumbnail_url": "https://instagram.com/p/gaming_003/media",
            "url": "https://instagram.com/p/gaming_003/",
            "scores": {
                "virality": 0.65,
                "relevance": 0.91,
                "final_score": 14.2
            },
            "niche_match": ["gaming", "pro"],
            "reactability": 0.75
        }
    ]
    
    data_access.add_movements(sample_movements)
    return data_access


if __name__ == "__main__":
    # Demo the data access system
    print("🗄️ Viral Movements Data Access Demo")
    print("=" * 40)
    
    # Create sample data
    data_access = create_sample_data()
    
    # Show all movements
    all_movements = data_access.get_all_movements()
    print(f"📊 Total movements: {len(all_movements)}")
    
    # Filter examples
    print(f"\n🔍 Filter Examples:")
    
    # High score movements
    high_score = data_access.get_movements_by_score(min_score=15)
    print(f"• High score movements (>15): {len(high_score)}")
    
    # YouTube movements
    youtube_movements = data_access.get_movements_by_platform("youtube")
    print(f"• YouTube movements: {len(youtube_movements)}")
    
    # Trending movements
    trending = data_access.get_trending_movements(growth_threshold=3.0)
    print(f"• Trending movements (>3x growth): {len(trending)}")
    
    # Search by keywords
    gaming_movements = data_access.search_movements(["gaming"])
    print(f"• Gaming movements: {len(gaming_movements)}")
    
    # Show summary
    summary = data_access.get_summary()
    print(f"\n📈 Summary:")
    print(f"• Total movements: {summary['statistics']['total_movements']}")
    print(f"• Average score: {summary['statistics']['avg_score']:.2f}")
    print(f"• High score movements: {summary['statistics']['high_score_movements']}")
    print(f"• Platforms: {summary['statistics']['platforms']}")
    
    # Export example
    success = data_access.export_movements("sample_export.json", filters={"min_score": 15})
    print(f"\n💾 Export successful: {success}")
    
    print(f"\n✅ Data access system ready!")
    print(f"📁 Data file: viral_movements_data.json")
    print(f"📁 Export file: sample_export.json")