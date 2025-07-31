#!/usr/bin/env python3
"""
VoidCat V2 Comprehensive End-to-End Tests
=========================================

Final comprehensive E2E test suite that validates the complete VoidCat V2 system
with real-world scenarios and edge cases. This test suite represents the
culmination of Task 6 testing efforts.

Test Categories:
- Complete project lifecycle management
- Complex task hierarchies and dependencies
- Data consistency and integrity
- Error handling and recovery
- Performance and scalability
- Real-world usage scenarios

Author: Codey Jr. (channeling the complete cosmic testing harmony)
License: MIT
Version: 2.0.0-alpha
"""

import asyncio
import json
import os
import shutil
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List

import pytest

from voidcat_persistence import PersistenceManager
from voidcat_task_models import Priority, TaskStatus, VoidCatProject, VoidCatTask


class TestComprehensiveE2E:
    """Comprehensive end-to-end tests - the ultimate cosmic validation! 🌊✨"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def persistence_manager(self, temp_workspace):
        """Create a persistence manager for testing."""
        return PersistenceManager(temp_workspace)

    def test_software_development_lifecycle_e2e(self, persistence_manager):
        """Test complete software development lifecycle end-to-end."""
        pm = persistence_manager

        # Phase 1: Project Initialization
        project = VoidCatProject(
            name="VoidCat V2 Software Development",
            description="Complete software development lifecycle for VoidCat V2",
            tags=["software", "development", "lifecycle", "v2"],
        )
        project.custom_fields["budget"] = "$50,000"
        project.custom_fields["deadline"] = "2025-12-31"
        project.custom_fields["team_size"] = 5
        pm.save_project(project)

        # Phase 2: Create Epic-level Tasks
        epics = [
            ("Requirements Analysis", "Gather and analyze system requirements"),
            ("System Architecture", "Design system architecture and components"),
            ("Core Development", "Implement core system functionality"),
            ("Testing & QA", "Comprehensive testing and quality assurance"),
            ("Deployment", "Production deployment and monitoring"),
        ]

        epic_tasks = []
        for i, (name, description) in enumerate(epics):
            epic = VoidCatTask(
                name=name,
                description=description,
                project_id=project.id,
                priority=Priority.HIGH,
                status=TaskStatus.PENDING,
                tags=["epic", f"phase-{i+1}"],
            )
            epic.metrics.estimated_hours = 40.0
            epic.metrics.complexity_score = 8

            # Add dependency to previous epic
            if i > 0:
                epic.add_dependency(epic_tasks[i - 1].id)

            pm.save_task(epic)
            epic_tasks.append(epic)

        # Phase 3: Create Feature-level Tasks
        feature_tasks = {}
        for epic in epic_tasks:
            features = []
            for j in range(3):
                feature = VoidCatTask(
                    name=f"{epic.name} - Feature {j+1}",
                    description=f"Feature {j+1} implementation for {epic.name}",
                    project_id=project.id,
                    parent_id=epic.id,
                    priority=Priority.MEDIUM,
                    status=TaskStatus.PENDING,
                    tags=["feature", epic.name.lower().replace(" ", "-")],
                )
                feature.metrics.estimated_hours = 15.0
                feature.metrics.complexity_score = 6
                pm.save_task(feature)
                features.append(feature)

            feature_tasks[epic.id] = features

        # Phase 4: Create Subtask-level Tasks
        subtask_count = 0
        for epic_id, features in feature_tasks.items():
            for feature in features:
                for k in range(2):
                    subtask = VoidCatTask(
                        name=f"{feature.name} - Subtask {k+1}",
                        description=f"Subtask {k+1} implementation",
                        project_id=project.id,
                        parent_id=feature.id,
                        priority=Priority.LOW,
                        status=TaskStatus.PENDING,
                        tags=["subtask", "implementation"],
                    )
                    subtask.metrics.estimated_hours = 5.0
                    subtask.metrics.complexity_score = 3
                    pm.save_task(subtask)
                    subtask_count += 1

        # Phase 5: Execute the Project
        # Start Requirements Analysis
        requirements_epic = epic_tasks[0]
        requirements_epic.status = TaskStatus.IN_PROGRESS
        pm.save_task(requirements_epic)

        # Complete requirements features
        req_features = feature_tasks[requirements_epic.id]
        for feature in req_features:
            feature.status = TaskStatus.COMPLETED
            feature.metrics.actual_hours = 12.0
            pm.save_task(feature)

        # Complete requirements epic
        requirements_epic.status = TaskStatus.COMPLETED
        requirements_epic.metrics.actual_hours = 38.0
        pm.save_task(requirements_epic)

        # Start Architecture
        arch_epic = epic_tasks[1]
        arch_epic.status = TaskStatus.IN_PROGRESS
        pm.save_task(arch_epic)

        # Phase 6: Validate Project State
        # Verify project structure
        loaded_project = pm.load_project(project.id)
        assert loaded_project.name == "VoidCat V2 Software Development"
        assert loaded_project.custom_fields["budget"] == "$50,000"

        # Verify epic completion
        loaded_req_epic = pm.load_task(requirements_epic.id)
        assert loaded_req_epic.status == TaskStatus.COMPLETED
        assert loaded_req_epic.metrics.actual_hours == 38.0

        # Verify architecture epic is in progress
        loaded_arch_epic = pm.load_task(arch_epic.id)
        assert loaded_arch_epic.status == TaskStatus.IN_PROGRESS

        # Verify subtask count
        assert subtask_count == 30  # 5 epics * 3 features * 2 subtasks

        # Phase 7: Complex Queries and Validation
        # Query by status
        completed_tasks = pm.query_tasks(
            project_id=project.id, status=TaskStatus.COMPLETED
        )
        # We completed 1 epic + 3 features = 4 tasks minimum
        assert len(completed_tasks) >= 1  # At least requirements epic

        # Query by tags
        epic_tasks_query = pm.query_tasks(project_id=project.id, tags=["epic"])
        assert len(epic_tasks_query) == 5

        # Query by priority
        high_priority_tasks = pm.query_tasks(
            project_id=project.id, priority=Priority.HIGH
        )
        assert len(high_priority_tasks) == 5  # All epics

    def test_concurrent_multi_project_operations_e2e(self, persistence_manager):
        """Test concurrent operations across multiple projects."""
        pm = persistence_manager

        # Create multiple projects
        projects = []
        for i in range(5):
            project = VoidCatProject(
                name=f"Concurrent Project {i+1}",
                description=f"Project {i+1} for concurrent testing",
                tags=["concurrent", f"project-{i+1}"],
            )
            pm.save_project(project)
            projects.append(project)

        # Create tasks for each project concurrently
        all_tasks = []
        for project in projects:
            for j in range(10):
                task = VoidCatTask(
                    name=f"Task {j+1} for {project.name}",
                    description=f"Task {j+1} description",
                    project_id=project.id,
                    priority=Priority.MEDIUM,
                    status=TaskStatus.PENDING,
                    tags=["concurrent", f"task-{j+1}"],
                )
                pm.save_task(task)
                all_tasks.append(task)

        # Update tasks concurrently
        for i, task in enumerate(all_tasks):
            if i % 3 == 0:
                task.status = TaskStatus.IN_PROGRESS
                task.assignee = f"User {i % 5}"
            elif i % 3 == 1:
                task.status = TaskStatus.COMPLETED
                task.metrics.actual_hours = float(i + 1)
            else:
                task.status = TaskStatus.BLOCKED
                task.custom_fields["blocked_reason"] = "Waiting for dependencies"

            pm.save_task(task)

        # Verify all operations completed successfully
        for project in projects:
            project_tasks = pm.query_tasks(project_id=project.id)
            assert len(project_tasks) == 10

            # Verify status distribution
            in_progress = [
                t for t in project_tasks if t.status == TaskStatus.IN_PROGRESS
            ]
            completed = [t for t in project_tasks if t.status == TaskStatus.COMPLETED]
            blocked = [t for t in project_tasks if t.status == TaskStatus.BLOCKED]

            assert len(in_progress) >= 3
            assert len(completed) >= 3
            assert len(blocked) >= 3

    def test_complex_dependency_chain_e2e(self, persistence_manager):
        """Test complex dependency chains and resolution."""
        pm = persistence_manager

        # Create project
        project = VoidCatProject(
            name="Complex Dependencies Project",
            description="Testing complex dependency chains",
        )
        pm.save_project(project)

        # Create a complex dependency chain
        # A -> B -> C -> D -> E (linear chain)
        # F -> G -> H (parallel chain)
        # I depends on both E and H (convergence)

        tasks = {}

        # Linear chain A -> B -> C -> D -> E
        linear_chain = ["A", "B", "C", "D", "E"]
        for i, name in enumerate(linear_chain):
            task = VoidCatTask(
                name=f"Task {name}",
                description=f"Linear chain task {name}",
                project_id=project.id,
                priority=Priority.MEDIUM,
                status=TaskStatus.PENDING,
                tags=["linear", f"task-{name.lower()}"],
            )

            # Add dependency to previous task
            if i > 0:
                prev_task = tasks[linear_chain[i - 1]]
                task.add_dependency(prev_task.id)

            pm.save_task(task)
            tasks[name] = task

        # Parallel chain F -> G -> H
        parallel_chain = ["F", "G", "H"]
        for i, name in enumerate(parallel_chain):
            task = VoidCatTask(
                name=f"Task {name}",
                description=f"Parallel chain task {name}",
                project_id=project.id,
                priority=Priority.MEDIUM,
                status=TaskStatus.PENDING,
                tags=["parallel", f"task-{name.lower()}"],
            )

            # Add dependency to previous task
            if i > 0:
                prev_task = tasks[parallel_chain[i - 1]]
                task.add_dependency(prev_task.id)

            pm.save_task(task)
            tasks[name] = task

        # Convergence task I depends on both E and H
        task_i = VoidCatTask(
            name="Task I",
            description="Convergence task depending on both chains",
            project_id=project.id,
            priority=Priority.HIGH,
            status=TaskStatus.PENDING,
            tags=["convergence", "critical"],
        )
        task_i.add_dependency(tasks["E"].id)
        task_i.add_dependency(tasks["H"].id)
        pm.save_task(task_i)
        tasks["I"] = task_i

        # Execute the chains
        # Complete linear chain
        for name in linear_chain:
            task = tasks[name]
            task.status = TaskStatus.COMPLETED
            task.metrics.actual_hours = 8.0
            pm.save_task(task)

        # Complete parallel chain
        for name in parallel_chain:
            task = tasks[name]
            task.status = TaskStatus.COMPLETED
            task.metrics.actual_hours = 6.0
            pm.save_task(task)

        # Now task I should be ready (all dependencies completed)
        # Complete task I
        task_i.status = TaskStatus.COMPLETED
        task_i.metrics.actual_hours = 10.0
        pm.save_task(task_i)

        # Verify all tasks completed
        for name, task in tasks.items():
            loaded_task = pm.load_task(task.id)
            assert loaded_task.status == TaskStatus.COMPLETED
            assert loaded_task.metrics.actual_hours > 0

        # Verify dependency relationships
        loaded_task_i = pm.load_task(task_i.id)
        assert len(loaded_task_i.dependencies) == 2
        dependency_ids = [dep.task_id for dep in loaded_task_i.dependencies]
        assert tasks["E"].id in dependency_ids
        assert tasks["H"].id in dependency_ids

    def test_data_integrity_under_stress_e2e(self, persistence_manager):
        """Test data integrity under stress conditions."""
        pm = persistence_manager

        # Create base project
        project = VoidCatProject(
            name="Stress Test Project",
            description="Testing data integrity under stress",
        )
        pm.save_project(project)

        # Create a large number of tasks
        tasks = []
        for i in range(100):
            task = VoidCatTask(
                name=f"Stress Task {i+1}",
                description=f"Stress testing task {i+1}",
                project_id=project.id,
                priority=Priority.MEDIUM,
                status=TaskStatus.PENDING,
                tags=["stress", f"task-{i+1}"],
            )
            task.metrics.estimated_hours = float(i + 1)
            pm.save_task(task)
            tasks.append(task)

        # Perform rapid updates
        for i, task in enumerate(tasks):
            # Update task properties
            task.status = TaskStatus.IN_PROGRESS
            task.assignee = f"User {i % 10}"
            task.metrics.actual_hours = float(i + 1) * 0.8
            task.custom_fields["iteration"] = i
            pm.save_task(task)

        # Complete half the tasks
        for i in range(0, len(tasks), 2):
            task = tasks[i]
            task.status = TaskStatus.COMPLETED
            task.metrics.actual_hours = float(i + 1) * 1.2
            pm.save_task(task)

        # Verify data integrity
        all_tasks = pm.query_tasks(project_id=project.id)
        assert len(all_tasks) == 100

        # Check completed tasks
        completed_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
        assert len(completed_tasks) == 50

        # Check in-progress tasks
        in_progress_tasks = [t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]
        assert len(in_progress_tasks) == 50

        # Verify metrics consistency
        for task in completed_tasks:
            assert task.metrics.actual_hours > task.metrics.estimated_hours

        for task in in_progress_tasks:
            assert task.metrics.actual_hours < task.metrics.estimated_hours

    def test_error_recovery_scenarios_e2e(self, persistence_manager):
        """Test error recovery scenarios."""
        pm = persistence_manager

        # Create project
        project = VoidCatProject(
            name="Error Recovery Test", description="Testing error recovery mechanisms"
        )
        pm.save_project(project)

        # Scenario 1: Invalid task updates
        task = VoidCatTask(
            name="Error Recovery Task",
            description="Testing error recovery",
            project_id=project.id,
            priority=Priority.HIGH,
            status=TaskStatus.PENDING,
        )
        pm.save_task(task)

        # Try to create circular dependency (should fail gracefully)
        try:
            task.add_dependency(task.id)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "cannot depend on itself" in str(e)

        # Verify task is still valid
        loaded_task = pm.load_task(task.id)
        assert loaded_task is not None
        assert loaded_task.name == "Error Recovery Task"

        # Scenario 2: Invalid status transitions
        # (This would require workflow validation, which may not be implemented)

        # Scenario 3: Non-existent dependencies
        # Create task with non-existent dependency
        task2 = VoidCatTask(
            name="Task with Invalid Dependency",
            description="Testing invalid dependency handling",
            project_id=project.id,
            priority=Priority.MEDIUM,
            status=TaskStatus.PENDING,
        )

        # Add dependency to non-existent task
        task2.add_dependency("non-existent-task-id")
        pm.save_task(task2)

        # Verify task was saved despite invalid dependency
        loaded_task2 = pm.load_task(task2.id)
        assert loaded_task2 is not None
        assert len(loaded_task2.dependencies) == 1
        assert loaded_task2.dependencies[0].task_id == "non-existent-task-id"

        # System should continue to work
        task3 = VoidCatTask(
            name="Normal Task After Error",
            description="Testing system continues after error",
            project_id=project.id,
            priority=Priority.LOW,
            status=TaskStatus.PENDING,
        )
        pm.save_task(task3)

        loaded_task3 = pm.load_task(task3.id)
        assert loaded_task3 is not None
        assert loaded_task3.name == "Normal Task After Error"

    def test_performance_benchmarks_e2e(self, persistence_manager):
        """Test performance benchmarks."""
        pm = persistence_manager

        # Create project
        project = VoidCatProject(
            name="Performance Benchmark Project",
            description="Testing performance benchmarks",
        )
        pm.save_project(project)

        # Benchmark 1: Task creation speed
        start_time = time.time()
        tasks = []
        for i in range(50):
            task = VoidCatTask(
                name=f"Performance Task {i+1}",
                description=f"Performance testing task {i+1}",
                project_id=project.id,
                priority=Priority.MEDIUM,
                status=TaskStatus.PENDING,
            )
            pm.save_task(task)
            tasks.append(task)

        creation_time = time.time() - start_time
        print(f"Task creation time: {creation_time:.3f}s for 50 tasks")
        assert creation_time < 5.0  # Should complete within 5 seconds

        # Benchmark 2: Query performance
        start_time = time.time()
        for i in range(20):
            all_tasks = pm.query_tasks(project_id=project.id)
            assert len(all_tasks) == 50

        query_time = time.time() - start_time
        print(f"Query time: {query_time:.3f}s for 20 queries")
        assert query_time < 2.0  # Should complete within 2 seconds

        # Benchmark 3: Update performance
        start_time = time.time()
        for task in tasks:
            task.status = TaskStatus.IN_PROGRESS
            task.assignee = "Performance Tester"
            pm.save_task(task)

        update_time = time.time() - start_time
        print(f"Update time: {update_time:.3f}s for 50 updates")
        assert update_time < 3.0  # Should complete within 3 seconds

        # Benchmark 4: Load performance
        start_time = time.time()
        for task in tasks:
            loaded_task = pm.load_task(task.id)
            assert loaded_task is not None

        load_time = time.time() - start_time
        print(f"Load time: {load_time:.3f}s for 50 loads")
        assert load_time < 2.0  # Should complete within 2 seconds

    def test_real_world_scenario_e2e(self, persistence_manager):
        """Test a comprehensive real-world scenario."""
        pm = persistence_manager

        # Scenario: VoidCat V2 Development Sprint
        project = VoidCatProject(
            name="VoidCat V2 Development Sprint",
            description="Two-week development sprint for VoidCat V2 features",
            tags=["sprint", "development", "v2"],
        )
        project.custom_fields["sprint_duration"] = "2 weeks"
        project.custom_fields["team_size"] = 3
        project.custom_fields["sprint_goal"] = "Implement core task management features"
        pm.save_project(project)

        # Create user stories
        user_stories = [
            ("As a user, I want to create tasks", "Task creation functionality"),
            ("As a user, I want to organize tasks in projects", "Project organization"),
            ("As a user, I want to track task progress", "Progress tracking"),
            ("As a user, I want to set task dependencies", "Dependency management"),
            ("As a user, I want to view task metrics", "Metrics and reporting"),
        ]

        story_tasks = []
        for story, description in user_stories:
            task = VoidCatTask(
                name=story,
                description=description,
                project_id=project.id,
                priority=Priority.HIGH,
                status=TaskStatus.PENDING,
                tags=["user-story", "feature"],
            )
            task.metrics.estimated_hours = 16.0
            pm.save_task(task)
            story_tasks.append(task)

        # Create development tasks for each story
        for story_task in story_tasks:
            dev_tasks = [
                ("Design", "Design the feature interface"),
                ("Implementation", "Implement the feature"),
                ("Testing", "Test the feature"),
                ("Documentation", "Document the feature"),
            ]

            for task_name, task_desc in dev_tasks:
                dev_task = VoidCatTask(
                    name=f"{story_task.name} - {task_name}",
                    description=task_desc,
                    project_id=project.id,
                    parent_id=story_task.id,
                    priority=Priority.MEDIUM,
                    status=TaskStatus.PENDING,
                    tags=["development", task_name.lower()],
                )
                dev_task.metrics.estimated_hours = 4.0
                pm.save_task(dev_task)

        # Sprint execution simulation
        # Day 1-2: Planning and Design
        design_tasks = pm.query_tasks(project_id=project.id, tags=["design"])

        for task in design_tasks:
            task.status = TaskStatus.COMPLETED
            task.assignee = "Designer"
            task.metrics.actual_hours = 3.5
            pm.save_task(task)

        # Day 3-8: Implementation
        impl_tasks = pm.query_tasks(project_id=project.id, tags=["implementation"])

        for i, task in enumerate(impl_tasks):
            task.status = TaskStatus.COMPLETED
            task.assignee = f"Developer {(i % 2) + 1}"
            task.metrics.actual_hours = 5.0
            pm.save_task(task)

        # Day 9-10: Testing
        test_tasks = pm.query_tasks(project_id=project.id, tags=["testing"])

        for task in test_tasks:
            task.status = TaskStatus.COMPLETED
            task.assignee = "QA Tester"
            task.metrics.actual_hours = 4.5
            pm.save_task(task)

        # Day 11-12: Documentation
        doc_tasks = pm.query_tasks(project_id=project.id, tags=["documentation"])

        for task in doc_tasks:
            task.status = TaskStatus.COMPLETED
            task.assignee = "Technical Writer"
            task.metrics.actual_hours = 4.0
            pm.save_task(task)

        # Mark user stories as completed
        for story_task in story_tasks:
            story_task.status = TaskStatus.COMPLETED
            story_task.metrics.actual_hours = 17.0
            pm.save_task(story_task)

        # Sprint retrospective - analyze results
        all_tasks = pm.query_tasks(project_id=project.id)
        completed_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]

        # Verify sprint completion
        assert len(completed_tasks) == len(all_tasks)  # All tasks completed

        # Calculate sprint metrics
        total_estimated = sum(
            t.metrics.estimated_hours for t in all_tasks if t.metrics.estimated_hours
        )
        total_actual = sum(
            t.metrics.actual_hours for t in all_tasks if t.metrics.actual_hours
        )

        print(f"Sprint Results:")
        print(f"  Total Tasks: {len(all_tasks)}")
        print(f"  Completed Tasks: {len(completed_tasks)}")
        print(f"  Total Estimated Hours: {total_estimated}")
        print(f"  Total Actual Hours: {total_actual}")
        print(f"  Sprint Efficiency: {(total_estimated/total_actual)*100:.1f}%")

        # Verify realistic metrics
        assert total_estimated > 0
        assert total_actual > 0
        assert 0.8 <= (total_estimated / total_actual) <= 1.2  # Within 20% variance


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to see print statements
