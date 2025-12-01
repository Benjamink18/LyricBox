"""Test a single large batch to see limits."""
import asyncio
from fast_adaptive_test import AdaptiveBatchTest
import json

async def test_large_batch():
    tester = AdaptiveBatchTest()
    
    print("🧪 Testing single large batch...")
    print(f"📊 Current database: 1322 songs")
    print(f"📈 Remaining to import: ~1936 songs\n")
    
    # Test with 500 songs
    print("Testing 500 songs in one batch...")
    result = await tester.test_batch_size(500, song_offset=1322)
    
    print(f"\n{'✅' if not result['rate_limited'] else '❌'} Result:")
    print(f"  Batch size: {result['batch_size']}")
    print(f"  Duration: {result['avg_duration']:.1f}s")
    print(f"  Songs processed: {result['total_songs']}")
    print(f"  Rate limited: {result['rate_limited']}")
    
    if not result['rate_limited']:
        print("\n🎉 500 works! Want to try 1000?")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_large_batch())
    
    with open('large_batch_test_result.json', 'w') as f:
        json.dump(result, f, indent=2)
