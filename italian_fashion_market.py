#!/usr/bin/env python3
"""
ITALIAN FASHION MARKET SEGMENTS ANALYSIS
========================================
Phase 2 of ModaMesh™: Market Intelligence Foundation

Comprehensive analysis module for Italian fashion market segments and brands.
Provides endpoints for brand-segment relationships and market intelligence.

Phase 2 of ModaMesh: Market Intelligence Foundation
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SegmentCharacteristics:
    """Data class for segment characteristics"""
    segment_name: str
    definition: str
    functionality_score: float
    fashion_score: float
    brand_count: int

@dataclass
class BrandSegmentInfo:
    """Data class for brand segment information"""
    brand_name: str
    segments: List[SegmentCharacteristics]

class ItalianFashionMarket:
    """
    Italian Fashion Market Analysis Module
    
    Provides comprehensive market intelligence for Italian fashion brands
    and their segment positioning across the fashion-function spectrum.
    """
    
    def __init__(self, data_file: str = "data/italian_fashion_market.json"):
        """
        Initialize the Italian Fashion Market module
        
        Args:
            data_file (str): Path to the fashion market data JSON file
        """
        self.data_file = Path(data_file)
        self.market_data = {}
        self.brand_to_segments = {}
        self._load_market_data()
        self._build_brand_index()
    
    def _load_market_data(self) -> None:
        """Load market data from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.market_data = json.load(f)
            logger.info(f"✅ Loaded {len(self.market_data)} market segments from {self.data_file}")
        except FileNotFoundError:
            logger.error(f"❌ Market data file not found: {self.data_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in market data file: {e}")
            raise
    
    def _build_brand_index(self) -> None:
        """Build reverse index: brand -> segments"""
        self.brand_to_segments = {}
        
        for segment_name, segment_data in self.market_data.items():
            brands = segment_data.get('brands', [])
            for brand in brands:
                if brand not in self.brand_to_segments:
                    self.brand_to_segments[brand] = []
                self.brand_to_segments[brand].append(segment_name)
        
        logger.info(f"✅ Built brand index for {len(self.brand_to_segments)} unique brands")
    
    def get_all_brands(self) -> List[str]:
        """
        Get all brands in the Italian fashion market
        
        Returns:
            List[str]: Sorted list of all unique brands
        """
        return sorted(list(self.brand_to_segments.keys()))
    
    def get_brand_segments(self, brand_name: str) -> Optional[BrandSegmentInfo]:
        """
        Get segments and characteristics for a specific brand
        
        Args:
            brand_name (str): Name of the brand to query
            
        Returns:
            Optional[BrandSegmentInfo]: Brand segment information or None if brand not found
        """
        if brand_name not in self.brand_to_segments:
            logger.warning(f"⚠️  Brand '{brand_name}' not found in market data")
            return None
        
        segment_characteristics = []
        for segment_name in self.brand_to_segments[brand_name]:
            segment_data = self.market_data[segment_name]
            characteristics = SegmentCharacteristics(
                segment_name=segment_name,
                definition=segment_data['definition'],
                functionality_score=segment_data['functionality_score'],
                fashion_score=segment_data['fashion_score'],
                brand_count=len(segment_data['brands'])
            )
            segment_characteristics.append(characteristics)
        
        return BrandSegmentInfo(
            brand_name=brand_name,
            segments=segment_characteristics
        )
    
    def get_segment_characteristics(self, segment_name: str) -> Optional[SegmentCharacteristics]:
        """
        Get characteristics for a specific segment
        
        Args:
            segment_name (str): Name of the segment to query
            
        Returns:
            Optional[SegmentCharacteristics]: Segment characteristics or None if segment not found
        """
        if segment_name not in self.market_data:
            logger.warning(f"⚠️  Segment '{segment_name}' not found in market data")
            return None
        
        segment_data = self.market_data[segment_name]
        return SegmentCharacteristics(
            segment_name=segment_name,
            definition=segment_data['definition'],
            functionality_score=segment_data['functionality_score'],
            fashion_score=segment_data['fashion_score'],
            brand_count=len(segment_data['brands'])
        )
    
    def get_segment_brands(self, segment_name: str) -> Optional[List[str]]:
        """
        Get all brands that belong to a specific segment
        
        Args:
            segment_name (str): Name of the segment to query
            
        Returns:
            Optional[List[str]]: Sorted list of brands in the segment or None if segment not found
        """
        if segment_name not in self.market_data:
            logger.warning(f"⚠️  Segment '{segment_name}' not found in market data")
            return None
        
        return sorted(self.market_data[segment_name]['brands'])
    
    def get_all_segments(self) -> List[str]:
        """
        Get all segment names
        
        Returns:
            List[str]: List of all segment names
        """
        return list(self.market_data.keys())
    
    def get_market_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive market overview
        
        Returns:
            Dict[str, Any]: Market overview statistics
        """
        total_brands = len(self.brand_to_segments)
        total_segments = len(self.market_data)
        
        # Calculate segment statistics
        segment_stats = []
        for segment_name, segment_data in self.market_data.items():
            segment_stats.append({
                'segment': segment_name,
                'brand_count': len(segment_data['brands']),
                'functionality_score': segment_data['functionality_score'],
                'fashion_score': segment_data['fashion_score'],
                'definition': segment_data['definition']
            })
        
        # Sort by fashion-function balance (highest combined score first)
        segment_stats.sort(key=lambda x: x['functionality_score'] + x['fashion_score'], reverse=True)
        
        # Brand distribution analysis
        brand_distribution = {}
        for brand, segments in self.brand_to_segments.items():
            segment_count = len(segments)
            if segment_count not in brand_distribution:
                brand_distribution[segment_count] = 0
            brand_distribution[segment_count] += 1
        
        return {
            'total_brands': total_brands,
            'total_segments': total_segments,
            'segment_statistics': segment_stats,
            'brand_distribution': brand_distribution,
            'multi_segment_brands': {
                brand: segments for brand, segments in self.brand_to_segments.items() 
                if len(segments) > 1
            }
        }
    
    def find_similar_brands(self, target_brand: str, functionality_tolerance: float = 0.2, 
                           fashion_tolerance: float = 0.2) -> List[Dict[str, Any]]:
        """
        Find brands similar to the target brand based on segment positioning
        
        Args:
            target_brand (str): Brand to find similarities for
            functionality_tolerance (float): Tolerance for functionality score difference
            fashion_tolerance (float): Tolerance for fashion score difference
            
        Returns:
            List[Dict[str, Any]]: List of similar brands with similarity metrics
        """
        target_info = self.get_brand_segments(target_brand)
        if not target_info:
            return []
        
        # Calculate average scores for target brand
        target_func_avg = sum(s.functionality_score for s in target_info.segments) / len(target_info.segments)
        target_fashion_avg = sum(s.fashion_score for s in target_info.segments) / len(target_info.segments)
        
        similar_brands = []
        
        for brand in self.get_all_brands():
            if brand == target_brand:
                continue
                
            brand_info = self.get_brand_segments(brand)
            if not brand_info:
                continue
            
            # Calculate average scores for comparison brand
            brand_func_avg = sum(s.functionality_score for s in brand_info.segments) / len(brand_info.segments)
            brand_fashion_avg = sum(s.fashion_score for s in brand_info.segments) / len(brand_info.segments)
            
            # Check if within tolerance
            func_diff = abs(target_func_avg - brand_func_avg)
            fashion_diff = abs(target_fashion_avg - brand_fashion_avg)
            
            if func_diff <= functionality_tolerance and fashion_diff <= fashion_tolerance:
                # Calculate shared segments
                target_segments = set(s.segment_name for s in target_info.segments)
                brand_segments = set(s.segment_name for s in brand_info.segments)
                shared_segments = target_segments.intersection(brand_segments)
                
                similarity_score = len(shared_segments) / len(target_segments.union(brand_segments))
                
                similar_brands.append({
                    'brand': brand,
                    'functionality_score': brand_func_avg,
                    'fashion_score': brand_fashion_avg,
                    'functionality_difference': func_diff,
                    'fashion_difference': fashion_diff,
                    'shared_segments': list(shared_segments),
                    'similarity_score': similarity_score
                })
        
        # Sort by similarity score (highest first)
        similar_brands.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_brands

def main():
    """Example usage and testing of the Italian Fashion Market module"""
    print("🇮🇹 ITALIAN FASHION MARKET ANALYSIS")
    print("=" * 50)
    
    # Initialize the market module
    market = ItalianFashionMarket()
    
    # Test 1: Get all brands
    print(f"\n📋 ALL BRANDS ({len(market.get_all_brands())} total):")
    all_brands = market.get_all_brands()
    for i, brand in enumerate(all_brands[:10], 1):  # Show first 10
        print(f"   {i:2d}. {brand}")
    if len(all_brands) > 10:
        print(f"   ... and {len(all_brands) - 10} more brands")
    
    # Test 2: Get brand segments for Macron
    print(f"\n🎯 MACRON SEGMENT ANALYSIS:")
    macron_info = market.get_brand_segments("Macron")
    if macron_info:
        print(f"   Brand: {macron_info.brand_name}")
        print(f"   Segments: {len(macron_info.segments)}")
        for segment in macron_info.segments:
            print(f"   • {segment.segment_name}")
            print(f"     Definition: {segment.definition}")
            print(f"     Functionality: {segment.functionality_score:.1f} | Fashion: {segment.fashion_score:.1f}")
            print(f"     Total brands in segment: {segment.brand_count}")
    
    # Test 3: Get segment characteristics
    print(f"\n🏆 HIGH-PERFORMANCE LUXURY SEGMENT:")
    luxury_segment = market.get_segment_characteristics("6. High-Performance Luxury")
    if luxury_segment:
        print(f"   Definition: {luxury_segment.definition}")
        print(f"   Functionality Score: {luxury_segment.functionality_score:.1f}")
        print(f"   Fashion Score: {luxury_segment.fashion_score:.1f}")
        print(f"   Brands in segment: {luxury_segment.brand_count}")
    
    # Test 4: Get brands in a segment
    print(f"\n👑 LUXURY FASHION BRANDS:")
    luxury_brands = market.get_segment_brands("7. Luxury Fashion")
    if luxury_brands:
        for i, brand in enumerate(luxury_brands[:8], 1):  # Show first 8
            print(f"   {i}. {brand}")
        if len(luxury_brands) > 8:
            print(f"   ... and {len(luxury_brands) - 8} more luxury brands")
    
    # Test 5: Market overview
    print(f"\n📊 MARKET OVERVIEW:")
    overview = market.get_market_overview()
    print(f"   Total Brands: {overview['total_brands']}")
    print(f"   Total Segments: {overview['total_segments']}")
    print(f"   Multi-segment Brands: {len(overview['multi_segment_brands'])}")
    
    # Test 6: Find similar brands to Macron
    print(f"\n🔍 BRANDS SIMILAR TO MACRON:")
    similar = market.find_similar_brands("Macron", functionality_tolerance=0.3, fashion_tolerance=0.3)
    for i, brand_info in enumerate(similar[:5], 1):  # Show top 5
        print(f"   {i}. {brand_info['brand']} (similarity: {brand_info['similarity_score']:.2f})")
        print(f"      Func: {brand_info['functionality_score']:.1f} | Fashion: {brand_info['fashion_score']:.1f}")
        print(f"      Shared segments: {', '.join(brand_info['shared_segments'])}")
    
    print(f"\n✅ Italian Fashion Market Analysis Complete!")

if __name__ == "__main__":
    main() 