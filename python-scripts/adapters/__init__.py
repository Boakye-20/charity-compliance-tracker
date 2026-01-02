"""Source adapters for charity compliance data."""

from .base import BaseAdapter, NormalizedRecord, SourceMetadata
from .charity_commission import CharityCommissionAdapter
from .ico import ICOAdapter
from .charity_guidance import CharityGuidanceAdapter
from .hse import HSEAdapter
from .hmrc import HMRCAdapter
from .fundraising_regulator import FundraisingRegulatorAdapter
from .safeguarding import SafeguardingAdapter
from .data_protection import DataProtectionAdapter
from .financial_reporting import FinancialReportingAdapter
from .risk_management import RiskManagementAdapter
from .anti_fraud import AntiFraudAdapter

__all__ = [
    'BaseAdapter',
    'NormalizedRecord', 
    'SourceMetadata',
    'CharityCommissionAdapter',
    'ICOAdapter',
    'CharityGuidanceAdapter',
    'HSEAdapter',
    'HMRCAdapter',
    'FundraisingRegulatorAdapter',
    'SafeguardingAdapter',
    'DataProtectionAdapter',
    'FinancialReportingAdapter',
    'RiskManagementAdapter',
    'AntiFraudAdapter',
]
