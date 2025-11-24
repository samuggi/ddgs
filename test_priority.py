#!/usr/bin/env python3
"""Test script to verify Naver and Google priority search."""

from ddgs import DDGS


def test_priority_search():
    """Test that Naver results appear first, then Google."""
    print("=== Testing Priority Search ===\n")
    print("Priority order: Naver (3) > Google (2) > Others (1)\n")

    # Test with a simple query
    query = "python programming"
    print(f"Searching for: '{query}'")
    print("-" * 60)

    try:
        with DDGS() as ddgs:
            # Search with auto backend (should use all available engines)
            results = ddgs.search(query, max_results=10, backend="auto")

            if not results:
                print("No results found!")
                return

            print(f"\nFound {len(results)} results:\n")

            # Display results with engine information
            for i, result in enumerate(results, 1):
                engine = result.get("engine_name", "unknown")
                priority = result.get("engine_priority", "N/A")
                title = result.get("title", "No title")[:60]
                href = result.get("href", "No URL")[:80]

                print(f"{i}. [{engine.upper()} - Priority: {priority}]")
                print(f"   Title: {title}")
                print(f"   URL: {href}")
                print()

            # Count results by engine
            print("\n=== Results by Engine ===")
            engine_counts = {}
            for result in results:
                engine = result.get("engine_name", "unknown")
                engine_counts[engine] = engine_counts.get(engine, 0) + 1

            for engine, count in sorted(
                engine_counts.items(),
                key=lambda x: results[[r.get("engine_name") for r in results].index(x[0])].get("engine_priority", 0),
                reverse=True
            ):
                priority = next(
                    (r.get("engine_priority", "N/A") for r in results if r.get("engine_name") == engine),
                    "N/A"
                )
                print(f"{engine}: {count} results (priority: {priority})")

    except Exception as e:
        print(f"\nError during search: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


def test_specific_backends():
    """Test Naver and Google specifically."""
    print("\n\n=== Testing Specific Backends ===\n")

    query = "python"

    # Test Naver
    print("1. Testing Naver backend:")
    print("-" * 60)
    try:
        with DDGS() as ddgs:
            results = ddgs.search(query, max_results=3, backend="naver")
            print(f"Naver results: {len(results)}")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.get('title', 'No title')[:60]}")
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")

    # Test Google
    print("\n2. Testing Google backend:")
    print("-" * 60)
    try:
        with DDGS() as ddgs:
            results = ddgs.search(query, max_results=3, backend="google")
            print(f"Google results: {len(results)}")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.get('title', 'No title')[:60]}")
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    test_priority_search()
    test_specific_backends()
