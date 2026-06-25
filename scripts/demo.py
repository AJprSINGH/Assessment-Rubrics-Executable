#!/usr/bin/env python3
"""
Demo script for Assessment Rubric Agent v0.1
Tests the complete rubric generation workflow
"""

import sys
sys.path.insert(0, 'src')

import asyncio
from datetime import datetime

from assessment_rubric_agent.core.schemas.contracts import (
    RubricGenerationRequest, AssignmentInformation, ContextIntelligence
)
from assessment_rubric_agent.core.schemas.intelligence_objects import (
    Board, Subject, AssessmentType, RubricType
)
from assessment_rubric_agent.core.workflows.rubric_workflow import RubricGenerationWorkflow


async def main():
    """Run a demo rubric generation"""
    print("=" * 60)
    print("Assessment Rubric Agent v0.1 - Demo")
    print("=" * 60)
    
    # Initialize workflow
    csv_path = "/workspace/semantic_intelligence.csv"
    workflow = RubricGenerationWorkflow(csv_path)
    print(f"\n✓ Workflow initialized")
    
    # Create request
    request = RubricGenerationRequest(
        request_id="demo-001",
        assignment=AssignmentInformation(
            board=Board.CBSE,
            grade=10,
            subject=Subject.SCIENCE,
            unit="Chemical Reactions",
            chapter="Chemical Reactions and Equations",
            assignment_name="Chemical Reactions Investigation Project",
            project_type="Research & Design Project",
            assessment_type=AssessmentType.PROJECT,
            rubric_type=RubricType.ANALYTICAL,
            total_marks=50,
            performance_scale=["Exemplary", "Proficient", "Developing", "Beginning"]
        ),
        context=ContextIntelligence(
            class_size=35,
            student_profile="Mixed ability",
            time_duration="2 weeks",
            available_resources=["Textbook", "Lab equipment", "Internet"],
            differentiation_required=True
        ),
        include_teacher_notes=True,
        include_student_checklist=True,
        generate_json=True,
        generate_pdf=True,
        cio_centric_mode=True
    )
    print(f"✓ Request created: {request.request_id}")
    print(f"  Board: {request.assignment.board}")
    print(f"  Grade: {request.assignment.grade}")
    print(f"  Subject: {request.assignment.subject}")
    print(f"  Chapter: {request.assignment.chapter}")
    print(f"  Total Marks: {request.assignment.total_marks}")
    
    # Execute workflow
    print("\n⏳ Generating rubric...")
    start_time = datetime.now()
    
    try:
        response = await workflow.execute(request)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        
        print(f"\n✓ Status: {response.status}")
        print(f"✓ Generation Time: {duration:.2f} seconds")
        print(f"✓ Alignment Coverage: {response.alignment_coverage:.1f}%")
        
        if response.teacher_rubric_pdf_path:
            print(f"✓ Teacher PDF: {response.teacher_rubric_pdf_path}")
        
        if response.student_rubric_pdf_path:
            print(f"✓ Student PDF: {response.student_rubric_pdf_path}")
        
        if response.rubric_matrix:
            print(f"\n✓ Rubric Matrix Generated:")
            print(f"  Rubric ID: {response.rubric_matrix.rubric_id}")
            print(f"  Criteria Count: {len(response.rubric_matrix.criteria)}")
            print(f"  Performance Levels: {len(response.rubric_matrix.performance_levels)}")
            
            print("\n  Criteria:")
            for criterion in response.rubric_matrix.criteria:
                print(f"    - {criterion.criterion_name}: {criterion.total_marks} marks")
                print(f"      Bloom Level: {criterion.blooms_level}")
        
        if response.errors:
            print(f"\n⚠ Errors: {response.errors}")
        
        if response.warnings:
            print(f"\n⚠ Warnings: {response.warnings}")
        
        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
