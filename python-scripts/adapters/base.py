"""
Base adapter interface that all source adapters must implement.
This ensures consistent behavior across different data sources.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@dataclass
class SourceMetadata:
    """Information about a data source."""
    name: str
    url: str
    regulator: str
    update_frequency: str  # "daily", "weekly", "monthly", "quarterly"
    last_fetched: Optional[datetime] = None
    record_count: int = 0


@dataclass
class NormalizedRecord:
    """
    A single record normalized to the common schema.
    Maps directly to CharityPolicy TypeScript interface.
    """
    id: str
    title: str
    summary: str
    source_url: str
    published_date: str
    last_updated: str
    regulator: str
    domain: str
    document_type: str
    
    # Optional fields
    charity_number: Optional[str] = None
    charity_name: Optional[str] = None
    charity_income_band: Optional[str] = None
    risk_level: Optional[str] = None
    case_id: Optional[str] = None
    case_status: Optional[str] = None
    outcome: Optional[str] = None
    issues_identified: Optional[list[str]] = None
    sanctions_regime: Optional[str] = None
    designated_by: Optional[str] = None
    fine_amount: Optional[float] = None
    keywords: Optional[list[str]] = None
    full_text: Optional[str] = None
    
    def to_csv_row(self) -> dict:
        """Convert to dictionary suitable for CSV writing."""
        row = {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'source_url': self.source_url,
            'published_date': self.published_date,
            'last_updated': self.last_updated,
            'regulator': self.regulator,
            'domain': self.domain,
            'document_type': self.document_type,
            'charity_number': self.charity_number or '',
            'charity_name': self.charity_name or '',
            'charity_income_band': self.charity_income_band or '',
            'risk_level': self.risk_level or '',
            'case_id': self.case_id or '',
            'case_status': self.case_status or '',
            'outcome': self.outcome or '',
            'issues_identified': '|'.join(self.issues_identified) if self.issues_identified else '',
            'sanctions_regime': self.sanctions_regime or '',
            'designated_by': self.designated_by or '',
            'fine_amount': str(self.fine_amount) if self.fine_amount else '',
            'keywords': '|'.join(self.keywords) if self.keywords else '',
        }
        return row


class BaseAdapter(ABC):
    """
    Abstract base class for all source adapters.
    
    Each adapter is responsible for:
    1. Downloading raw data from its source
    2. Normalizing records to the common schema
    3. Providing metadata about the source
    """
    
    def __init__(self, staging_dir: Path):
        """
        Initialize adapter with staging directory path.
        
        Args:
            staging_dir: Directory to store raw downloaded data
        """
        self.staging_dir = staging_dir
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def get_metadata(self) -> SourceMetadata:
        """Return metadata about this source."""
        pass
    
    @abstractmethod
    def download_raw(self) -> Path:
        """
        Download raw data from source to staging directory.
        
        Returns:
            Path to the downloaded file(s)
            
        Raises:
            Exception if download fails
        """
        pass
    
    @abstractmethod
    def normalize(self, raw_path: Path) -> list[NormalizedRecord]:
        """
        Convert raw data to normalized records.
        
        Args:
            raw_path: Path to raw data file
            
        Returns:
            List of normalized records
        """
        pass
    
    def fetch_and_normalize(self) -> list[NormalizedRecord]:
        """
        Complete pipeline: download then normalize.
        
        This is the main method called by the orchestrator.
        """
        self.logger.info(f"Starting fetch for {self.get_metadata().name}")
        
        try:
            raw_path = self.download_raw()
            self.logger.info(f"Downloaded to {raw_path}")
            
            records = self.normalize(raw_path)
            self.logger.info(f"Normalized {len(records)} records")
            
            return records
            
        except Exception as e:
            self.logger.error(f"Failed to fetch {self.get_metadata().name}: {e}")
            raise
