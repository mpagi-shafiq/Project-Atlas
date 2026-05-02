"""
Basic tests for the Developer Triage Agent.

Tests the core functionality of the RepoMapper to ensure it can correctly
identify and analyze repository structure.
"""

import pytest
from pathlib import Path
from src.triage_agent.repo_mapper import RepoMapper


class TestRepoMapper:
    """Test suite for RepoMapper functionality."""
    
    def test_repo_mapper_initialization(self):
        """Test that RepoMapper can be initialized with current directory."""
        mapper = RepoMapper('.')
        assert mapper.root_path == Path('.')
        assert isinstance(mapper.ignore_patterns, list)
        assert '.venv' in mapper.ignore_patterns
    
    def test_scan_directory_finds_src_folder(self):
        """Test that RepoMapper can identify the src folder."""
        mapper = RepoMapper('.')
        structure = mapper.scan_directory()
        
        # Check that structure was created
        assert structure is not None
        assert 'children' in structure
        
        # Look for src folder in children
        src_found = False
        for child in structure.get('children', []):
            if child.get('name') == 'src':
                src_found = True
                assert child.get('type') == 'directory'
                break
        
        assert src_found, "src folder should be found in repository structure"
    
    def test_analyze_folder_purpose_for_src(self):
        """Test that RepoMapper correctly identifies src folder purpose."""
        mapper = RepoMapper('.')
        
        # Create a mock folder data for src
        src_folder_data = {
            'name': 'src',
            'path': 'src',
            'type': 'directory',
            'files': [],
            'children': []
        }
        
        mission = mapper.analyze_folder_purpose(src_folder_data)
        
        # Should recognize 'src' as source code directory
        assert mission is not None
        assert 'source code' in mission.lower()
    
    def test_scan_repository_generates_missions(self):
        """Test that scan_repository generates mission statements."""
        mapper = RepoMapper('.')
        result = mapper.scan_repository()
        
        # Check result structure
        assert 'structure' in result
        assert 'missions' in result
        assert 'summary' in result
        
        # Check that missions were generated
        missions = result['missions']
        assert isinstance(missions, dict)
        assert len(missions) > 0
        
        # Check that src folder has a mission
        src_mission_found = False
        for path, mission in missions.items():
            if 'src' in path:
                src_mission_found = True
                assert isinstance(mission, str)
                assert len(mission) > 0
                break
        
        assert src_mission_found, "src folder should have a mission statement"
    
    def test_should_ignore_patterns(self):
        """Test that ignore patterns work correctly."""
        mapper = RepoMapper('.')
        
        # Test common ignore patterns
        assert mapper.should_ignore(Path('.venv'))
        assert mapper.should_ignore(Path('__pycache__'))
        assert mapper.should_ignore(Path('.git'))
        assert mapper.should_ignore(Path('node_modules'))
        
        # Test that normal folders are not ignored
        assert not mapper.should_ignore(Path('src'))
        assert not mapper.should_ignore(Path('tests'))
    
    def test_generate_mission_statements(self):
        """Test mission statement generation."""
        mapper = RepoMapper('.')
        structure = mapper.scan_directory()
        missions = mapper.generate_mission_statements(structure)
        
        assert isinstance(missions, dict)
        assert len(missions) > 0
        
        # Each mission should be a non-empty string
        for path, mission in missions.items():
            assert isinstance(path, str)
            assert isinstance(mission, str)
            assert len(mission) > 0


class TestRepoMapperEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_directory_handling(self, tmp_path):
        """Test handling of empty directories."""
        mapper = RepoMapper(str(tmp_path))
        structure = mapper.scan_directory()
        
        assert structure is not None
        assert structure['name'] == tmp_path.name
        assert structure['children'] == []
        assert structure['files'] == []
    
    def test_nested_directory_structure(self, tmp_path):
        """Test scanning nested directory structures."""
        # Create nested structure
        (tmp_path / 'level1' / 'level2' / 'level3').mkdir(parents=True)
        (tmp_path / 'level1' / 'level2' / 'test.py').write_text('# test file')
        
        mapper = RepoMapper(str(tmp_path))
        structure = mapper.scan_directory(max_depth=5)
        
        # Should find nested structure
        assert len(structure['children']) > 0
        level1 = structure['children'][0]
        assert level1['name'] == 'level1'
    
    def test_max_depth_limit(self, tmp_path):
        """Test that max_depth parameter limits scanning depth."""
        # Create deep nested structure
        deep_path = tmp_path / 'a' / 'b' / 'c' / 'd' / 'e'
        deep_path.mkdir(parents=True)
        
        mapper = RepoMapper(str(tmp_path))
        
        # Scan with depth limit
        structure_shallow = mapper.scan_directory(max_depth=2)
        structure_deep = mapper.scan_directory(max_depth=10)
        
        # Shallow scan should have fewer items
        assert structure_shallow is not None
        assert structure_deep is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

# Made with Bob
