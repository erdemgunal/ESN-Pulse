import json
import os

def remove_duplicate_branches(data):
    """Remove duplicate branches from each country based on branch ID."""
    total_duplicates = 0
    
    for country in data["countries"]:
        # Track branch IDs we've seen
        seen_branch_ids = set()
        unique_branches = []
        
        for branch in country["branches"]:
            branch_id = branch["id"]
            if branch_id not in seen_branch_ids:
                seen_branch_ids.add(branch_id)
                unique_branches.append(branch)
            else:
                total_duplicates += 1
        
        # Replace with unique branches
        original_count = len(country["branches"])
        country["branches"] = unique_branches
        new_count = len(country["branches"])
        
        if original_count > new_count:
            print(f"Removed {original_count - new_count} duplicate(s) from {country['name']}")
    
    print(f"\nTotal duplicates removed: {total_duplicates}")
    return data

def main():
    # Input and output file paths
    input_path = '/Users/erdemgunal/Desktop/sites/esn/ESN Pulse/data/esn_data.json'
    output_path = input_path  # Overwrite the original file
    backup_path = input_path + '.backup'
    
    # Create backup of original file
    with open(input_path, 'r') as f:
        original_data = json.load(f)
    
    with open(backup_path, 'w') as f:
        json.dump(original_data, f, indent=2)
    
    print(f"Created backup at {backup_path}")
    
    # Clean the data
    cleaned_data = remove_duplicate_branches(original_data)
    
    # Save cleaned data
    with open(output_path, 'w') as f:
        json.dump(cleaned_data, f, indent=2)
    
    print(f"Cleaned data saved to {output_path}")
    
    # Update metadata
    if "metadata" in cleaned_data:
        print("\nUpdated metadata:")
        print(f"- Countries: {cleaned_data['metadata']['total_countries']}")
        
        # Count actual branches after removing duplicates
        total_branches = sum(len(country['branches']) for country in cleaned_data['countries'])
        cleaned_data['metadata']['total_branches'] = total_branches
        print(f"- Branches: {total_branches}")
        
        # Save again with updated metadata
        with open(output_path, 'w') as f:
            json.dump(cleaned_data, f, indent=2)

if __name__ == "__main__":
    main()