"""Test 500 songs in one batch to find real limits."""
import asyncio
from fast_adaptive_test import FastAdaptiveTest
import json
from datetime import datetime

async def test_500_batch():
    tester = FastAdaptiveTest()
    
    print("=" * 60)
    print("🧪 TESTING 500 SONGS IN ONE BATCH")
    print("=" * 60)
    print(f"📊 Current database: 1322 songs")
    print(f"📈 Remaining to import: ~1936 songs")
    print(f"⏱️  Estimated time: ~2 hours")
    print(f"🎯 Testing if Claude can handle 500 at once...")
    print("=" * 60)
    print()
    
    start_time = datetime.now()
    print(f"🚀 Starting at {start_time.strftime('%H:%M:%S')}\n")
    
    # Test with 500 songs starting from song 1322
    result = await tester.test_batch_size(500, song_offset=1322)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    if result['rate_limited']:
        print("❌ RATE LIMITED at 500 songs")
        print("=" * 60)
        print(f"  Duration: {duration/60:.1f} minutes")
        print(f"  Songs processed: {result['total_songs']}")
        print(f"  Conclusion: 500 is too many, optimal is probably 250-300")
    else:
        print("✅ 500 SONGS WORKED!")
        print("=" * 60)
        print(f"  Duration: {duration/60:.1f} minutes ({duration/60/60:.1f} hours)")
        print(f"  Songs processed: {result['total_songs']}")
        print(f"  Success rate: {result['total_songs']/500*100:.1f}%")
        print(f"\n💡 500 works! Could potentially try 1000 next...")
        print(f"   Full import (~1936 songs) would take ~{duration*1936/500/3600:.1f} hours at this rate")
    
    print("\n" + "=" * 60)
    
    # Save result
    result_data = {
        "batch_size": 500,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration,
        "rate_limited": result['rate_limited'],
        "total_songs": result['total_songs']
    }
    
    with open('test_500_result.json', 'w') as f:
        json.dump(result_data, f, indent=2)
    
    print(f"📝 Results saved to test_500_result.json")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_500_batch())
