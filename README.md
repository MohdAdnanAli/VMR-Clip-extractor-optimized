# 🎬 Viral Movements Analyzer with Enterprise Monitoring

A comprehensive viral movements detection and analysis system with enterprise-grade monitoring, performance tracking, and real-time observability.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Monitoring System](#monitoring-system)
- [Data Access](#data-access)
- [Configuration](#configuration)
- [Development](#development)
- [Production Deployment](#production-deployment)

## 🎯 Overview

This system analyzes viral movements from various platforms (YouTube, TikTok, Instagram) and identifies high-potential content for reaction videos. It includes a sophisticated monitoring system that tracks every aspect of the analysis process.

### What It Does
1. **Fetches trending movements** from multiple platforms
2. **Calculates virality scores** using engagement metrics
3. **Filters content** by relevance to your niche
4. **Deduplicates** similar content using image hashing
5. **Scores and ranks** movements for maximum viral potential
6. **Monitors everything** with real-time performance tracking

## ✨ Features

### 🔍 Core Analysis Features
- **Multi-Platform Support**: YouTube, TikTok, Instagram Reels
- **Virality Scoring**: Advanced algorithm considering views, engagement, velocity
- **Content Relevance**: AI-powered relevance matching to your niche
- **Duplicate Detection**: Image hash-based deduplication
- **Reactability Check**: Audio analysis to filter music-only content
- **Machine Learning**: Weekly feedback loop for weight optimization

### 📊 Monitoring & Observability
- **Function Execution Tracking**: Every function call logged with parameters
- **Performance Metrics**: Execution time, memory usage, CPU utilization
- **Real-time Events**: Live monitoring with event bus architecture
- **Progress Tracking**: Weighted progress steps with completion estimates
- **Error Handling**: Comprehensive error logging with stack traces
- **Data Retention**: 90-day detailed logs, 1-year summary data

### 🛠️ Technical Features
- **Asynchronous Monitoring**: Zero performance impact on main workflow
- **SQLite Database**: Structured data storage with indexing
- **Configuration Management**: Hot-reloadable JSON configuration
- **Event-Driven Architecture**: Decoupled components with message passing
- **Graceful Degradation**: System continues if monitoring fails

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Viral Movements Analyzer                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Fetch     │  │   Score     │  │     Filter &        │ │
│  │ Movements   │→ │ Movements   │→ │    Deduplicate      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Monitoring System                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Decorators  │→ │ Event Bus   │→ │    Database         │ │
│  │ (@monitor)  │  │ (Real-time) │  │   (SQLite)          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                              │                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │Performance  │  │   Logging   │  │   Configuration     │ │
│  │  Tracker    │  │   System    │  │    Manager          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Installation

### Prerequisites
```bash
# Python 3.7+
python --version

# Required packages
pip install pandas sentence-transformers whisper imagehash pillow requests yt-dlp scikit-learn psutil
```

### Setup
```bash
# Clone or download the project
git clone https://github.com/MohdAdnanAli/VMR-Clip-extractor-optimized
cd viral-movements-analyzer

# Install dependencies
pip install -r requirements.txt

# Initialize the system
python test_monitoring_demo.py
```

## ⚡ Quick Start

### 1. Basic Usage
```bash
# Run with monitoring
python main_with_monitoring.py

# Check results
ls -la *.xlsx *.db *.log
```

### 2. View Monitoring Data
```python
from monitoring.database import db_manager
from monitoring.models import LogFilters

# Get recent function calls
filters = LogFilters(limit=10)
logs = db_manager.query_log_entries(filters)

for log in logs:
    print(f"{log.function_name}: {log.duration:.3f}s")
```

### 3. Access Viral Movements Data
```python
from data_access import ViralMovementsDataAccess

# Initialize data access
data_access = ViralMovementsDataAccess()

# Get top movements by score
top_movements = data_access.get_movements_by_score(min_score=15, limit=5)

# Filter by platform
youtube_movements = data_access.filter_movements(platform="youtube")

# Get performance summary
summary = data_access.get_performance_summary()
```

## 📊 Monitoring System

### Components

#### 1. Function Decorators
```python
@monitor_all(weight=3.0)        # Complete monitoring
@monitor_execution              # Execution tracking only
@track_performance             # Performance metrics only
```

#### 2. Event System
- **Real-time events**: `function.started`, `function.completed`, `function.failed`
- **Progress events**: `progress.step_started`, `progress.step_completed`
- **Performance events**: `performance.recorded`, `performance.threshold_exceeded`

#### 3. Data Storage
- **Log Entries**: Function calls, parameters, results, errors
- **Performance Metrics**: Execution time, memory usage, success rates
- **Configuration**: Hot-reloadable settings

### Monitoring Features

| Feature | Description | Status |
|---------|-------------|--------|
| Function Tracking | Log all function calls with parameters | ✅ Active |
| Performance Metrics | Execution time, memory, CPU usage | ✅ Active |
| Error Logging | Stack traces, context, parameters | ✅ Active |
| Progress Tracking | Weighted steps, completion estimates | ✅ Active |
| Real-time Events | Live monitoring via event bus | ✅ Active |
| Data Retention | 90-day logs, 1-year summaries | ✅ Active |

## 🗄️ Data Access

### Viral Clip Data Structure
```json
{
  "clips": [
    {
      "id": "video_123",
      "title": "Epic Gaming Moment",
      "platform": "youtube",
      "views": 150000,
      "views_last_24h": 25000,
      "likes": 8500,
      "comments": 1200,
      "shares": 450,
      "age_hours": 6.5,
      "growth_6h": 4.2,
      "transcript": "Amazing gameplay with funny moments",
      "thumbnail_url": "https://...",
      "url": "https://youtube.com/watch?v=...",
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
  }
}
```

### Data Access Methods
```python
# Filter by score range
high_score_clips = data_access.get_clips_by_score(min_score=15, max_score=25)

# Filter by platform
platform_clips = data_access.filter_clips(platform="youtube")

# Filter by time range
recent_clips = data_access.get_clips_by_timeframe(hours=24)

# Get trending clips
trending = data_access.get_trending_clips(growth_threshold=3.0)

# Export data
data_access.export_clips("clips_export.json", format="json")
```

## ⚙️ Configuration

### monitoring_config.json
```json
{
  "log_level": "INFO",
  "database_path": "monitoring.db",
  "log_file_path": "monitoring.log",
  "max_log_file_size": 10485760,
  "log_retention_days": 90,
  "summary_retention_days": 365,
  "dashboard_port": 5000,
  "update_interval": 5,
  "performance_threshold_multiplier": 1.5,
  "error_rate_threshold": 0.1,
  "alerts": [
    {
      "name": "fetch_failure",
      "condition": "event_type == 'fetch_failed'",
      "threshold": 1.0,
      "time_window": 2,
      "notification_channels": ["file", "console"]
    }
  ]
}
```

### viral_clips_config.json
```json
{
  "niche_keywords": ["gaming", "memes", "funny"],
  "platforms": ["youtube", "tiktok", "instagram"],
  "scoring_weights": {
    "views": 0.4,
    "velocity": 0.3,
    "engagement": 0.2,
    "relevance": 0.1
  },
  "filters": {
    "min_growth_rate": 3.0,
    "min_final_score": 15.0,
    "max_age_hours": 48
  }
}
```

## 🔧 Development

### Project Structure
```
viral-clip-analyzer/
├── main.py                     # Original viral clip analyzer
├── main_with_monitoring.py     # Monitored version
├── data_access.py             # Data access layer
├── README.md                  # This file
├── requirements.txt           # Dependencies
├── monitoring/                # Monitoring system
│   ├── __init__.py
│   ├── config.py             # Configuration management
│   ├── core.py               # System coordinator
│   ├── database.py           # SQLite operations
│   ├── decorators.py         # Function decorators
│   ├── event_bus.py          # Event system
│   ├── logging_setup.py      # Logging configuration
│   └── models.py             # Data models
├── tests/                    # Test files
│   ├── test_monitoring_demo.py
│   ├── test_monitoring_setup.py
│   └── test_complete_system.py
└── data/                     # Data files
    ├── monitoring.db         # SQLite database
    ├── monitoring.log        # Log file
    ├── viral_clips_data.json # Clip data
    └── clip_selections.xlsx  # Excel output
```

### Adding New Features

#### 1. Add Monitoring to New Functions
```python
from monitoring.decorators import monitor_all

@monitor_all(weight=2.0)
def my_new_function():
    # Your code here
    pass
```

#### 2. Add Custom Events
```python
from monitoring.event_bus import event_bus

# Publish custom event
event_bus.publish('custom.event', {
    'data': 'value',
    'timestamp': datetime.now().isoformat()
})

# Subscribe to events
def my_handler(event_type, data):
    print(f"Received: {event_type}")

event_bus.subscribe('custom.event', my_handler)
```

#### 3. Query Monitoring Data
```python
from monitoring.database import db_manager
from monitoring.models import LogFilters, TimeRange
from datetime import datetime, timedelta

# Query recent logs
filters = LogFilters(
    function_name="fetch_trending_clips",
    time_range=TimeRange(
        start=datetime.now() - timedelta(hours=1),
        end=datetime.now()
    )
)
logs = db_manager.query_log_entries(filters)
```

## 🚀 Production Deployment

### Performance Considerations
- **Monitoring Overhead**: <5% of total execution time
- **Memory Usage**: ~10MB additional for monitoring
- **Database Size**: ~1MB per 1000 function calls
- **Log Rotation**: Automatic cleanup after retention period

### Scaling
- **Horizontal**: Multiple instances with shared database
- **Vertical**: Increase memory for larger datasets
- **Storage**: Regular database maintenance and archiving

### Monitoring in Production
```bash
# Check system status
python -c "from monitoring.core import monitoring_system; print(monitoring_system.get_status())"

# View recent errors
tail -f monitoring.log | grep ERROR

# Database maintenance
python -c "from monitoring.database import db_manager; db_manager.cleanup_old_data()"
```

## 📈 Performance Metrics

### Benchmarks (Typical Run)
- **Clip Fetching**: ~0.2-0.5s per platform
- **Scoring**: ~0.01-0.05s per clip
- **Deduplication**: ~0.1-0.3s per clip
- **Total Processing**: ~1-5s for 100 clips
- **Monitoring Overhead**: <0.1s additional

### Resource Usage
- **CPU**: 10-30% during processing
- **Memory**: 50-200MB peak usage
- **Disk**: 1-10MB per analysis session
- **Network**: Varies by platform API limits

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python test_monitoring_demo.py
python test_complete_system.py

# Check code quality
flake8 monitoring/
black monitoring/
```

### Adding Features
1. Create feature branch
2. Add monitoring decorators to new functions
3. Update configuration if needed
4. Add tests
5. Update documentation

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

### Common Issues
1. **Import Errors**: Install all dependencies with `pip install -r requirements.txt`
2. **Database Locked**: Close other connections to monitoring.db
3. **Memory Issues**: Reduce batch size or increase system memory
4. **API Limits**: Implement rate limiting for platform APIs

### Getting Help
- Check the logs: `tail -f monitoring.log`
- Run diagnostics: `python test_monitoring_demo.py`
- Review configuration: `cat monitoring_config.json`

---

**🎉 Ready to analyze viral clips with enterprise-grade monitoring!**

Built with ❤️ for content creators who want to stay ahead of viral trends.