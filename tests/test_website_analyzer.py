#!/usr/bin/env python3
"""
Core POC: Website Scanner + AI Analysis
Proves we can fetch, extract, and analyze websites to recommend automations.
"""
import asyncio
import sys
import json
from datetime import datetime

sys.path.insert(0, '/app/backend')

from analyzer.website_fetcher import fetch_and_extract_website
from analyzer.ai_analyzer import analyze_website_for_automations
from analyzer.schema import WebsiteAnalysis, AutomationRecommendation

# Test URLs
TEST_URLS = [
    "https://www.example.com",  # Simple site
    "https://stripe.com",  # Service/SaaS
    "https://www.shopify.com",  # E-commerce platform
]

async def test_single_website(url: str):
    """Test analysis of a single website"""
    print(f"\n{'='*80}")
    print(f"Testing: {url}")
    print(f"{'='*80}")
    
    try:
        # Step 1: Fetch and extract
        print("\n[1/3] Fetching and extracting website...")
        start = datetime.now()
        extraction = await fetch_and_extract_website(url)
        fetch_time = (datetime.now() - start).total_seconds()
        print(f"✓ Fetched in {fetch_time:.2f}s")
        print(f"  - Title: {extraction.title}")
        print(f"  - Business Type: {extraction.business_type}")
        print(f"  - Content Length: {len(extraction.content_text)} chars")
        print(f"  - Forms Found: {len(extraction.forms)}")
        print(f"  - CTAs Found: {len(extraction.ctas)}")
        
        # Step 2: AI Analysis
        print("\n[2/3] Running AI analysis...")
        start = datetime.now()
        analysis = await analyze_website_for_automations(extraction)
        analysis_time = (datetime.now() - start).total_seconds()
        print(f"✓ Analyzed in {analysis_time:.2f}s")
        
        # Step 3: Validate Results
        print("\n[3/3] Validation:")
        
        # Check recommendation count
        rec_count = len(analysis.recommendations)
        if rec_count >= 5:
            print(f"✓ Generated {rec_count} recommendations (≥5 required)")
        else:
            print(f"✗ Only {rec_count} recommendations (need ≥5)")
            return False
        
        # Check schema validity
        try:
            for rec in analysis.recommendations:
                assert rec.key, "Missing recommendation key"
                assert rec.title, "Missing recommendation title"
                assert rec.rationale, "Missing rationale"
                assert rec.expected_impact, "Missing expected impact"
                assert rec.category in ['agent', 'booking', 'marketing', 'lead_generation', 'social_media', 'analytics', 'automation'], f"Invalid category: {rec.category}"
            print("✓ All recommendations valid schema")
        except AssertionError as e:
            print(f"✗ Schema validation failed: {e}")
            return False
        
        # Check total time
        total_time = fetch_time + analysis_time
        if total_time <= 30:
            print(f"✓ Total time {total_time:.2f}s (≤30s required)")
        else:
            print(f"⚠ Total time {total_time:.2f}s (target ≤30s)")
        
        # Print recommendations
        print(f"\n{'─'*80}")
        print("RECOMMENDATIONS:")
        print(f"{'─'*80}")
        for i, rec in enumerate(analysis.recommendations, 1):
            print(f"\n{i}. {rec.title} [{rec.category}]")
            print(f"   Rationale: {rec.rationale[:100]}...")
            print(f"   Impact: {rec.expected_impact}")
            print(f"   Priority: {rec.priority}")
        
        print(f"\n{'='*80}")
        print(f"✓ SUCCESS: {url}")
        print(f"{'='*80}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {url}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run tests on all URLs"""
    print("\n" + "="*80)
    print("GR8 AI AUTOMATION - CORE POC TEST")
    print("Website Analyzer + AI Recommendations")
    print("="*80)
    
    results = []
    for url in TEST_URLS:
        success = await test_single_website(url)
        results.append((url, success))
    
    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for url, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {url}")
    
    print(f"\nResults: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Core POC validated!")
        print("Ready to build app around proven core.\n")
        return 0
    else:
        print("\n⚠ SOME TESTS FAILED - Fix issues before proceeding.\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
