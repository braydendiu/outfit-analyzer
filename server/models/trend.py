from pydantic import BaseModel
from typing import List, Dict

class TrendReport(BaseModel):
    trending_items: List[Dict]
    color_trends: List[Dict]
    style_categories: List[Dict]
    sentiment_analysis: Dict