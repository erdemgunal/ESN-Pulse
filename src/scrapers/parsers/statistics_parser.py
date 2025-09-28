from typing import Dict

def parse_detailed_statistics(activities_stats: Dict, category: str) -> Dict[str, Dict[str, int]]:
    result = {}
    
    for stat_type in ['total', 'physical', 'online']:
        key = f"{stat_type}_{category}"
        values = activities_stats.get(key, {}).get('values', [])
        
        for item in values:
            if len(item) >= 2:
                name = item[0]
                count = item[1]
                
                if name not in result:
                    result[name] = {}
                
                result[name][stat_type] = count
    
    return result