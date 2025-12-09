"""
Script to fetch all Apify Actors from the API and compile them into a list
with affiliate links.
"""

import requests
import json
import time
from typing import List, Dict

# Apify API endpoint
API_BASE_URL = "https://api.apify.com/v2/store"
AFFILIATE_PARAM = "?fpr=p2hrc6"

def fetch_all_actors(limit: int = 100) -> List[Dict]:
    """
    Fetch all actors from Apify Store API with pagination.
    
    Args:
        limit: Number of actors to fetch per request (max 100)
    
    Returns:
        List of all actors with their details
    """
    all_actors = []
    offset = 0
    total_fetched = 0
    
    print("Starting to fetch Apify Actors...")
    
    while True:
        try:
            # Make API request with pagination
            params = {
                "limit": limit,
                "offset": offset
            }
            
            response = requests.get(API_BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract actors from response
            actors = data.get("data", {}).get("items", [])
            
            if not actors:
                print(f"No more actors found at offset {offset}")
                break
            
            # Process each actor
            for actor in actors:
                actor_info = {
                    "name": actor.get("name", "Unknown"),
                    "username": actor.get("username", ""),
                    "title": actor.get("title", actor.get("name", "Unknown")),
                    "description": actor.get("description", ""),
                    "url": actor.get("url", ""),
                    "affiliate_url": "",
                    "stats": actor.get("stats", {}),
                    "categories": actor.get("categories", []),
                    "createdAt": actor.get("createdAt", ""),
                    "modifiedAt": actor.get("modifiedAt", "")
                }
                
                # Create affiliate URL
                if actor_info["url"]:
                    # Check if URL already has query parameters
                    separator = "&" if "?" in actor_info["url"] else "?"
                    actor_info["affiliate_url"] = f"{actor_info['url']}{separator}fpr=p2hrc6"
                else:
                    # Construct URL from username and name if URL is missing
                    if actor_info["username"] and actor_info["name"]:
                        actor_info["url"] = f"https://apify.com/{actor_info['username']}/{actor_info['name']}"
                        actor_info["affiliate_url"] = f"{actor_info['url']}?fpr=p2hrc6"
                
                all_actors.append(actor_info)
            
            total_fetched += len(actors)
            print(f"Fetched {total_fetched} actors so far... (offset: {offset})")
            
            # Check if we've reached the end
            total_count = data.get("data", {}).get("total", 0)
            if offset + len(actors) >= total_count:
                print(f"Reached end. Total actors: {total_count}")
                break
            
            offset += limit
            
            # Be respectful with API rate limits
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching actors at offset {offset}: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
            continue
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    
    print(f"\nTotal actors fetched: {len(all_actors)}")
    return all_actors

def save_to_json(actors: List[Dict], filename: str = "apify_actors.json"):
    """Save actors data to JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(actors, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(actors)} actors to {filename}")

def generate_markdown_list(actors: List[Dict], filename: str = "APIFY_ACTORS.md"):
    """Generate a markdown file with all actors and affiliate links."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Apify Actors List\n\n")
        f.write(f"Complete list of {len(actors)} Apify Actors (APIs) available on the Apify platform.\n\n")
        f.write("---\n\n")
        
        # Group by category if available
        actors_by_category = {}
        uncategorized = []
        
        for actor in actors:
            categories = actor.get("categories", [])
            if categories:
                for category in categories:
                    if category not in actors_by_category:
                        actors_by_category[category] = []
                    actors_by_category[category].append(actor)
            else:
                uncategorized.append(actor)
        
        # Write categorized actors
        if actors_by_category:
            for category in sorted(actors_by_category.keys()):
                f.write(f"## {category}\n\n")
                for actor in sorted(actors_by_category[category], key=lambda x: x.get("title", "")):
                    title = actor.get("title", actor.get("name", "Unknown"))
                    affiliate_url = actor.get("affiliate_url", actor.get("url", ""))
                    description = actor.get("description", "")
                    
                    if description:
                        f.write(f"- **[{title}]({affiliate_url})** - {description}\n")
                    else:
                        f.write(f"- **[{title}]({affiliate_url})**\n")
                f.write("\n")
        
        # Write uncategorized actors
        if uncategorized:
            f.write("## Uncategorized\n\n")
            for actor in sorted(uncategorized, key=lambda x: x.get("title", "")):
                title = actor.get("title", actor.get("name", "Unknown"))
                affiliate_url = actor.get("affiliate_url", actor.get("url", ""))
                description = actor.get("description", "")
                
                if description:
                    f.write(f"- **[{title}]({affiliate_url})** - {description}\n")
                else:
                    f.write(f"- **[{title}]({affiliate_url})**\n")
            f.write("\n")
        
        f.write("---\n\n")
        f.write(f"*Total: {len(actors)} Actors*\n")
        f.write(f"*Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    print(f"Generated markdown list: {filename}")

def generate_simple_list(actors: List[Dict], filename: str = "apify_actors_simple.txt"):
    """Generate a simple text file with just names and affiliate URLs."""
    with open(filename, "w", encoding="utf-8") as f:
        for actor in sorted(actors, key=lambda x: x.get("title", "")):
            title = actor.get("title", actor.get("name", "Unknown"))
            affiliate_url = actor.get("affiliate_url", actor.get("url", ""))
            f.write(f"{title}|{affiliate_url}\n")
    
    print(f"Generated simple list: {filename}")

if __name__ == "__main__":
    print("=" * 60)
    print("Apify Actors Fetcher")
    print("=" * 60)
    print()
    
    # Fetch all actors
    actors = fetch_all_actors(limit=100)
    
    if actors:
        # Save to JSON
        save_to_json(actors, "apify_actors.json")
        
        # Generate markdown list
        generate_markdown_list(actors, "APIFY_ACTORS.md")
        
        # Generate simple list
        generate_simple_list(actors, "apify_actors_simple.txt")
        
        print("\n" + "=" * 60)
        print("Done! All files have been generated.")
        print("=" * 60)
    else:
        print("No actors were fetched. Please check the API connection.")

