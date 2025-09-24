#!/usr/bin/env python3
"""
Quick Pinecone Management Script
Simple commands to manage your Pinecone index
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pinecone_manager import PineconeManager, load_qa_data_from_file
import json


def quick_truncate():
    """Quickly truncate the index"""
    try:
        manager = PineconeManager()
        print("Truncating Pinecone index...")
        success = manager.truncate_index()
        if success:
            print("✅ Index truncated successfully")
        else:
            print("❌ Failed to truncate index")
    except Exception as e:
        print(f"❌ Error: {e}")


def quick_populate():
    """Quickly populate the index with Q&A data"""
    try:
        manager = PineconeManager()
        print("Loading Q&A data...")
        qa_data = load_qa_data_from_file()
        print(f"Found {len(qa_data)} Q&A pairs")
        
        print("Populating Pinecone index...")
        success = manager.populate_with_qa_data(qa_data)
        if success:
            print(f"✅ Index populated successfully with {len(qa_data)} Q&A pairs")
        else:
            print("❌ Failed to populate index")
    except Exception as e:
        print(f"❌ Error: {e}")


def quick_reset():
    """Quickly truncate and populate the index"""
    try:
        manager = PineconeManager()
        
        print("Truncating Pinecone index...")
        truncate_success = manager.truncate_index()
        if not truncate_success:
            print("❌ Failed to truncate index")
            return
        
        print("Loading Q&A data...")
        qa_data = load_qa_data_from_file()
        print(f"Found {len(qa_data)} Q&A pairs")
        
        print("Populating Pinecone index...")
        populate_success = manager.populate_with_qa_data(qa_data)
        if populate_success:
            print(f"✅ Index reset and populated successfully with {len(qa_data)} Q&A pairs")
        else:
            print("❌ Failed to populate index")
    except Exception as e:
        print(f"❌ Error: {e}")


def show_stats():
    """Show current index statistics"""
    try:
        manager = PineconeManager()
        stats = manager.get_index_stats()
        print("Current Pinecone index stats:")
        print(json.dumps(stats, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")


def test_query(question):
    """Test a query against the index"""
    try:
        manager = PineconeManager()
        results = manager.test_query(question)
        print(f"Query: '{question}'")
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python pinecone_quick.py truncate    - Delete all vectors from index")
        print("  python pinecone_quick.py populate    - Add Q&A data to index")
        print("  python pinecone_quick.py reset       - Truncate and populate")
        print("  python pinecone_quick.py stats      - Show index statistics")
        print("  python pinecone_quick.py test <question> - Test a query")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "truncate":
        quick_truncate()
    elif command == "populate":
        quick_populate()
    elif command == "reset":
        quick_reset()
    elif command == "stats":
        show_stats()
    elif command == "test":
        if len(sys.argv) < 3:
            print("Please provide a question to test")
            sys.exit(1)
        question = " ".join(sys.argv[2:])
        test_query(question)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
