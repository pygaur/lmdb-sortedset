"""
Basic usage examples for LMDB SortedSet library.
"""

from lmdb_sortedset import LMDBSortedSet


def leaderboard_example():
    """Example: Game leaderboard with sorted set."""
    print("\n=== Leaderboard Example ===")
    
    with LMDBSortedSet(path="./data/leaderboard") as client:
        # Add players with their scores
        client.zadd("game:leaderboard", {
            "player1": 1500,
            "player2": 2300,
            "player3": 1800,
            "player4": 2100,
            "player5": 1200,
        })
        
        print(f"Total players: {client.zcard('game:leaderboard')}")
        
        # Get top 3 players
        print("\nTop 3 players:")
        top_players = client.zrange("game:leaderboard", -3, -1, withscores=True)
        top_players.reverse()  # Highest first
        for rank, (player, score) in enumerate(top_players, 1):
            print(f"  {rank}. {player}: {score}")
        
        # Get players in score range
        print("\nPlayers with scores between 1500-2000:")
        mid_range = client.zrangebyscore("game:leaderboard", 1500, 2000, withscores=True)
        for player, score in mid_range:
            print(f"  {player}: {score}")
        
        # Update a player's score
        client.zadd("game:leaderboard", {"player1": 2500})
        print(f"\nUpdated player1's score to: {client.zscore('game:leaderboard', 'player1')}")
        
        # Remove a player
        client.zrem("game:leaderboard", "player5")
        print(f"Removed player5. Total players now: {client.zcard('game:leaderboard')}")


def priority_queue_example():
    """Example: Priority queue using sorted set."""
    print("\n=== Priority Queue Example ===")
    
    with LMDBSortedSet(path="./data/tasks") as client:
        # Add tasks with priorities (lower score = higher priority)
        client.zadd("tasks:pending", {
            "task1: Send email": 3,
            "task2: Fix bug": 1,
            "task3: Review PR": 2,
            "task4: Update docs": 5,
            "task5: Deploy": 1,
        })
        
        print(f"Total pending tasks: {client.zcard('tasks:pending')}")
        
        # Process top 3 highest priority tasks
        print("\nProcessing top 3 priority tasks:")
        tasks = client.zpopmin("tasks:pending", count=3)
        for task, priority in tasks:
            print(f"  Processing: {task} (priority: {priority})")
        
        print(f"\nRemaining tasks: {client.zcard('tasks:pending')}")
        
        # Show remaining tasks
        remaining = client.zrange("tasks:pending", 0, -1, withscores=True)
        for task, priority in remaining:
            print(f"  {task} (priority: {priority})")


def time_series_example():
    """Example: Time series data using scores as timestamps."""
    print("\n=== Time Series Example ===")
    
    import time
    
    with LMDBSortedSet(path="./data/events") as client:
        # Add events with timestamps
        base_time = time.time()
        client.zadd("user:123:events", {
            "login": base_time,
            "view_page_1": base_time + 10,
            "view_page_2": base_time + 30,
            "purchase": base_time + 60,
            "logout": base_time + 120,
        })
        
        print(f"Total events: {client.zcard('user:123:events')}")
        
        # Get events in chronological order
        print("\nEvents in chronological order:")
        events = client.zrange("user:123:events", 0, -1, withscores=True)
        for event, timestamp in events:
            print(f"  {event} at {timestamp:.2f}")
        
        # Get events in a time range
        time_range_start = base_time + 20
        time_range_end = base_time + 80
        print(f"\nEvents between timestamps {time_range_start:.2f} and {time_range_end:.2f}:")
        range_events = client.zrangebyscore("user:123:events", time_range_start, time_range_end)
        for event in range_events:
            print(f"  {event}")
        
        # Remove old events (older than 50 seconds)
        cutoff = base_time + 50
        removed = client.zremrangebyscore("user:123:events", 0, cutoff)
        print(f"\nRemoved {removed} old events")
        print(f"Remaining events: {client.zcard('user:123:events')}")


def cache_with_scores_example():
    """Example: Cache with access frequency tracking."""
    print("\n=== Cache with Frequency Tracking Example ===")
    
    with LMDBSortedSet(path="./data/cache") as client:
        # Add items with access counts
        client.zadd("cache:items", {
            "item1": 5,   # accessed 5 times
            "item2": 15,  # accessed 15 times
            "item3": 3,   # accessed 3 times
            "item4": 8,   # accessed 8 times
            "item5": 25,  # accessed 25 times
        })
        
        # Get least frequently accessed items (candidates for eviction)
        print("Least frequently accessed items (eviction candidates):")
        lfu_items = client.zrange("cache:items", 0, 2, withscores=True)
        for item, count in lfu_items:
            print(f"  {item}: {count} accesses")
        
        # Increment access count for an item
        current_count = client.zscore("cache:items", "item3")
        client.zadd("cache:items", {"item3": current_count + 1})
        print(f"\nIncremented item3 access count to: {client.zscore('cache:items', 'item3')}")
        
        # Get most frequently accessed items
        print("\nMost frequently accessed items:")
        mfu_items = client.zrange("cache:items", -3, -1, withscores=True)
        mfu_items.reverse()
        for item, count in mfu_items:
            print(f"  {item}: {count} accesses")


def rate_limiter_example():
    """Example: Rate limiter using sorted set with timestamps."""
    print("\n=== Rate Limiter Example ===")
    
    import time
    import uuid
    
    with LMDBSortedSet(path="./data/ratelimit") as client:
        user_id = "user:456"
        current_time = time.time()
        window_size = 60  # 60 seconds window
        max_requests = 10
        
        # Simulate some requests
        print(f"Simulating requests within a {window_size}s window:")
        for i in range(12):
            request_id = str(uuid.uuid4())
            request_time = current_time + (i * 2)  # 2 seconds apart
            
            # Add this request
            client.zadd(f"ratelimit:{user_id}", {request_id: request_time})
            
            # Remove old requests outside the window
            window_start = request_time - window_size
            client.zremrangebyscore(f"ratelimit:{user_id}", 0, window_start)
            
            # Check if rate limit exceeded
            request_count = client.zcard(f"ratelimit:{user_id}")
            status = "ALLOWED" if request_count <= max_requests else "BLOCKED"
            print(f"  Request {i+1}: {status} ({request_count}/{max_requests})")


def multiple_sorted_sets_example():
    """Example: Working with multiple sorted sets."""
    print("\n=== Multiple Sorted Sets Example ===")
    
    with LMDBSortedSet(path="./data/multi", key_prefix="myapp") as client:
        # Create multiple sorted sets
        client.zadd("scores:math", {"alice": 95, "bob": 87, "charlie": 92})
        client.zadd("scores:science", {"alice": 88, "bob": 91, "charlie": 85})
        client.zadd("scores:english", {"alice": 90, "bob": 93, "charlie": 88})
        
        # Get top student in each subject
        print("Top students by subject:")
        for subject in ["math", "science", "english"]:
            key = f"scores:{subject}"
            top_student = client.zpopmax(key, count=1)
            if top_student:
                name, score = top_student[0]
                print(f"  {subject.capitalize()}: {name} ({score})")
                # Put it back
                client.zadd(key, {name: score})


def main():
    """Run all examples."""
    print("LMDB SortedSet Library - Usage Examples")
    print("=" * 50)
    
    leaderboard_example()
    priority_queue_example()
    time_series_example()
    cache_with_scores_example()
    rate_limiter_example()
    multiple_sorted_sets_example()
    
    print("\n" + "=" * 50)
    print("Examples completed successfully!")


if __name__ == "__main__":
    main()


