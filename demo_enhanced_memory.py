#!/usr/bin/env python3
"""
VoidCat Enhanced Memory Storage Demo
===================================

Demo script showcasing the enhanced memory storage features:
- TF-IDF semantic search
- Intelligent archiving
- Advanced backup management

Author: Codey Jr. (with cosmic coding vibes)
"""

import tempfile
from pathlib import Path

from voidcat_memory_models import ImportanceLevel, MemoryCategory, MemoryFactory
from voidcat_memory_storage import MemoryStorageEngine, StorageConfig


def main():
    print("🌊 VoidCat Enhanced Memory Storage Demo")
    print("=" * 50)
    print("🧘‍♂️ Demonstrating cosmic coding vibes...")
    print()

    # Create temporary storage for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        config = StorageConfig(
            base_dir=Path(temp_dir) / "memory_storage",
            backup_dir=Path(temp_dir) / "memory_backups",
            index_dir=Path(temp_dir) / "memory_indexes",
            cache_size=50,
        )

        # Initialize enhanced storage engine
        engine = MemoryStorageEngine(config)
        print("✅ Enhanced Memory Storage Engine initialized")

        # Demo 1: Store some memories with different content
        print("\n📝 Demo 1: Storing diverse memories...")
        memories = [
            MemoryFactory.create_user_preference(
                key="coding_style",
                value="chill and zen-like",
                context="User prefers relaxed coding approach with Buddhist philosophy",
                importance=ImportanceLevel.HIGH,
            ),
            MemoryFactory.create_user_preference(
                key="favorite_language",
                value="Python",
                context="User loves Python for its simplicity and readability",
                importance=ImportanceLevel.MEDIUM,
            ),
            MemoryFactory.create_conversation_memory(
                session_id="demo_session_1",
                user_input="Can you explain machine learning algorithms?",
                assistant_response="Machine learning algorithms are computational methods that learn patterns from data...",
                importance=ImportanceLevel.MEDIUM,
            ),
            MemoryFactory.create_learned_heuristic(
                pattern_type="user_interaction",
                condition="User asks for code explanations",
                action="Provide step-by-step explanations with examples",
                importance=ImportanceLevel.HIGH,
            ),
        ]

        for memory in memories:
            memory.add_tag("demo")
            if "coding" in str(memory.to_dict()).lower():
                memory.add_tag("programming")
            if "python" in str(memory.to_dict()).lower():
                memory.add_tag("python")

            success = engine.store_memory(memory)
            print(f"  ✅ Stored: {memory.id[:8]}...")

        # Demo 2: Semantic search
        print("\n🔍 Demo 2: Semantic search capabilities...")
        search_queries = [
            "coding and programming",
            "Python language",
            "machine learning",
            "zen philosophy",
        ]

        for query in search_queries:
            results = engine.semantic_search(query, limit=3)
            print(f"  Query: '{query}' -> {len(results)} results")
            for memory, score in results:
                print(f"    📄 {memory.id[:8]}... (similarity: {score:.3f})")

        # Demo 3: Enhanced search with filters
        print("\n🎯 Demo 3: Enhanced search with filters...")
        from voidcat_memory_models import MemoryQuery

        query = MemoryQuery(
            text="programming",
            categories=[MemoryCategory.USER_PREFERENCES],
            tags=["programming"],
            importance_min=ImportanceLevel.MEDIUM,
        )

        results = engine.enhanced_search(query)
        print(f"  Enhanced search found {len(results)} filtered results")

        # Demo 4: Backup system
        print("\n💾 Demo 4: Advanced backup system...")
        backup_id = engine.create_full_backup("Demo full backup")
        print(f"  ✅ Full backup created: {backup_id}")

        # Add more memories for incremental backup
        new_memory = MemoryFactory.create_user_preference(
            key="backup_test",
            value="incremental backup demo",
            importance=ImportanceLevel.LOW,
        )
        engine.store_memory(new_memory)

        incremental_id = engine.create_incremental_backup("Demo incremental backup")
        if incremental_id:
            print(f"  ✅ Incremental backup created: {incremental_id}")
        else:
            print("  ℹ️ No changes for incremental backup")

        # Demo 5: Statistics
        print("\n📊 Demo 5: Enhanced statistics...")
        stats = engine.get_enhanced_statistics()
        print(f"  Total memories: {stats['total_memories']}")
        print(f"  TF-IDF features: {stats['memory_index_stats']['tfidf_features']}")
        print(f"  Cache hit rate: {stats['cache_hit_rate']:.1%}")
        print(f"  Backup count: {stats['backup_stats']['backup_count']}")

        # Demo 6: Archive simulation (normally based on age/access)
        print("\n🗄️ Demo 6: Archive capabilities...")
        archive_stats = engine.archiver.get_archive_statistics()
        print(f"  Archive ready - {archive_stats['archived_count']} memories archived")

        # Close engine
        engine.close()
        print("\n🌊 Demo completed successfully! The vibes are strong! ✨")


if __name__ == "__main__":
    main()
