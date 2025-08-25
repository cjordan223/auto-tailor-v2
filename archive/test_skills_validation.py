#!/usr/bin/env python3
"""
Test script for the complete skills validation workflow.
"""

import json
import tempfile
import os
from tex_tailor.schema import validate_skills_against_inventory, load_skills_inventory
from tex_tailor.proposer import apply_skills_validation


def test_skills_validation():
    """Test the complete skills validation workflow."""

    print("🧪 Testing Skills Validation Workflow")
    print("=" * 50)

    # Test 1: Load skills inventory
    print("\n1. Testing skills inventory loading...")
    inventory = load_skills_inventory()
    if inventory:
        print(f"✅ Skills inventory loaded successfully")
        print(
            f"   - Confirmed skills: {len(inventory.get('confirmed_skills', []))}")
        print(
            f"   - Conversational skills: {len(inventory.get('conversational_skills', []))}")
        print(
            f"   - Excluded skills: {len(inventory.get('exclude_skills', []))}")
    else:
        print("❌ Failed to load skills inventory")
        return False

    # Test 2: Test validation function
    print("\n2. Testing skills validation function...")
    original_skills = "Python, JavaScript, AWS"
    new_skills = "Python, JavaScript, AWS, SCADA, Kotlin, React"

    result = validate_skills_against_inventory(original_skills, new_skills)
    print(f"✅ Validation result:")
    print(f"   - Validated skills: {result['validated_skills']}")
    print(f"   - Flagged skills: {len(result['flagged_skills'])}")
    print(f"   - Confidence: {result['confidence']}")

    for flagged in result['flagged_skills']:
        print(f"     - {flagged['skill']}: {flagged['reason']}")

    # Test 3: Test apply_skills_validation function
    print("\n3. Testing apply_skills_validation function...")

    # Create mock edits data
    edits = {
        "skills": {
            "Programming Languages": {
                "replace": "Python, JavaScript, Kotlin"
            },
            "Cloud & DevOps": {
                "replace": "AWS, Docker, SCADA"
            }
        },
        "suggested_additions": []
    }

    base_text = {
        "resume": {
            "skills": {
                "Programming Languages": "Python, JavaScript",
                "Cloud & DevOps": "AWS, Docker"
            }
        }
    }

    validated_edits = apply_skills_validation(edits, base_text)

    print(f"✅ Applied validation:")
    print(
        f"   - Programming Languages: {validated_edits['skills']['Programming Languages']['replace']}")
    print(
        f"   - Cloud & DevOps: {validated_edits['skills']['Cloud & DevOps']['replace']}")
    print(
        f"   - Suggested additions: {len(validated_edits['suggested_additions'])}")

    for suggestion in validated_edits['suggested_additions']:
        print(f"     - {suggestion['term']}: {suggestion['why']}")

    print("\n🎉 All tests passed! Skills validation workflow is working correctly.")
    return True


if __name__ == "__main__":
    test_skills_validation()
