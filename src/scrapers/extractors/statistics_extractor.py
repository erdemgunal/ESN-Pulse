import json
import logging
from typing import Optional

from ...models.section_statistics import (
    SectionStatisticsModel,
    SectionOverallStatisticsModel,
    SectionCauseStatisticsModel,
    SectionTypeStatisticsModel,
    SectionParticipantStatisticsModel
)
from ..parsers.statistics_parser import parse_detailed_statistics

logger = logging.getLogger(__name__)

async def extract_section_statistics(
    http_client,
    activities_slug: str,
    base_url: str
) -> Optional[SectionStatisticsModel]:
    url = f"{base_url}/organisation/{activities_slug}/statistics"
    logger.info(f"Fetching statistics from: {url}")
    
    try:
        # Get and parse the HTML content
        content = await http_client.get_page_content(url)
        soup = await http_client.parse_html(content, url)
        
        # Find the Drupal settings script tag using selector
        drupal_settings = soup.select_one('script[type="application/json"][data-drupal-selector="drupal-settings-json"]')
        
        activities_stats = json.loads(drupal_settings.string)['activities_statistics']
        
        # Extract overall statistics
        total_activities = activities_stats.get('total_activities', {}).get('values', [])
        physical_activities = total_activities[0][1] if len(total_activities) > 0 else 0
        online_activities = total_activities[1][1] if len(total_activities) > 1 else 0
        
        total_participants = activities_stats.get('total_participants', {}).get('values', [])
        total_local_students = total_participants[0][1] if len(total_participants) > 0 else 0
        total_international_students = total_participants[1][1] if len(total_participants) > 1 else 0
        total_coordinators = total_participants[2][1] if len(total_participants) > 2 else 0
        
        # Extract detailed statistics
        cause_statistics = parse_detailed_statistics(activities_stats, 'causes')
        type_statistics = parse_detailed_statistics(activities_stats, 'types')
        participant_statistics = parse_detailed_statistics(activities_stats, 'participants')
        
        # Create overall statistics
        overall = SectionOverallStatisticsModel(
            section_id=0,  # Will be set when saving
            physical_activities=physical_activities,
            online_activities=online_activities,
            total_local_students=total_local_students,
            total_international_students=total_international_students,
            total_coordinators=total_coordinators
        )
        
        # Create cause statistics
        causes = []
        for cause_name, stats in cause_statistics.items():
            causes.append(SectionCauseStatisticsModel(
                section_id=0,
                cause_name=cause_name,
                total_count=stats.get('total', 0),
                physical_count=stats.get('physical', 0),
                online_count=stats.get('online', 0)
            ))
        
        # Create type statistics
        types = []
        for type_name, stats in type_statistics.items():
            types.append(SectionTypeStatisticsModel(
                section_id=0,
                activity_type=type_name,
                physical_count=stats.get('physical', 0),
                online_count=stats.get('online', 0)
            ))
        
        # Create participant statistics
        participants = []
        for participant_type, stats in participant_statistics.items():
            participants.append(SectionParticipantStatisticsModel(
                section_id=0,
                participant_type=participant_type,
                physical_count=stats.get('physical', 0),
                online_count=stats.get('online', 0)
            ))
        
        # Create the main statistics model
        statistics = SectionStatisticsModel(
            section_id=0,  # Will be set when saving
            overall=overall,
            causes=causes,
            types=types,
            participants=participants
        )
        
        return statistics
        
    except Exception as e:
        logger.error(f"Failed to extract statistics for {activities_slug}: {str(e)}")
        return None