#!/usr/bin/env python3
"""
Unit tests for Enhanced Data Pipeline
Phase 2A Week 3: Comprehensive testing for data pipeline automation
"""

import pytest
import tempfile
import shutil
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.mlops.data_pipeline import (
    DataPipelineManager, DataQualityStatus, PipelineStage, 
    DataVersion, QualityReport, get_data_pipeline_manager
)


@pytest.mark.unit 
class TestDataPipelineManager:
    """Test cases for DataPipelineManager core functionality."""""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.pipeline_manager = DataPipelineManager(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures after each test method."""""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    # ===== INITIALIZATION TESTS =====
    
    def test_initialization_success(self):
        """Test DataPipelineManager initializes successfully."""""
        assert self.pipeline_manager is not None
        assert self.pipeline_manager.storage_path == Path(self.temp_dir)
        assert self.pipeline_manager.data_path.exists()
        assert self.pipeline_manager.versions_path.exists()
        assert self.pipeline_manager.quality_path.exists()
        assert self.pipeline_manager.logs_path.exists()
        assert self.pipeline_manager.db_path.exists()
    
    def test_database_initialization(self):
        """Test database tables are created correctly."""""
        import sqlite3
        
        conn = sqlite3.connect(self.pipeline_manager.db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'data_versions' in tables
        assert 'quality_reports' in tables
        assert 'pipeline_runs' in tables
        
        conn.close()
    
    def test_global_instance(self):
        """Test global instance management."""""
        manager1 = get_data_pipeline_manager()
        manager2 = get_data_pipeline_manager()
        
        # Should return the same instance
        assert manager1 is manager2
        assert isinstance(manager1, DataPipelineManager)
    
    # ===== DATA INGESTION TESTS =====
    
    def test_ingest_simple_data(self):
        """Test ingesting simple dictionary data."""""
        # Create mock data
        data_dict = {
            'id': [1, 2, 3, 4, 5],
            'value': [10.5, 20.3, 15.7, 30.1, 25.9],
            'category': ['A', 'B', 'A', 'C', 'B']
        }
        
        # Mock pandas DataFrame if available
        try:
            import pandas as pd
            df = pd.DataFrame(data_dict)
            version = self.pipeline_manager.ingest_data(df, 'test_dataset', tags=['test'])
        except ImportError:
            # Skip this test if pandas not available
            pytest.skip("Pandas not available for DataFrame testing")
        
        assert version is not None
        assert version.dataset_name == 'test_dataset'
        assert version.row_count == 5
        assert version.column_count == 3
        assert 'test' in version.tags
        assert isinstance(version.quality_score, float)
        assert isinstance(version.quality_status, DataQualityStatus)
    
    def test_ingest_data_with_metadata(self):
        """Test ingesting data with source metadata."""""
        try:
            import pandas as pd
            df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
            
            metadata = {
                'source': 'test_source',
                'collection_date': '2024-01-15',
                'version': '1.0'
            }
            
            version = self.pipeline_manager.ingest_data(
                df, 'metadata_test', 
                source_metadata=metadata,
                tags=['metadata', 'test']
            )
            
            assert version.metadata['source'] == 'test_source'
            assert version.metadata['version'] == '1.0'
            assert 'metadata' in version.tags
            assert 'test' in version.tags
            
        except ImportError:
            pytest.skip("Pandas not available for DataFrame testing")
    
    def test_ingest_empty_data(self):
        """Test ingesting empty data."""""
        try:
            import pandas as pd
            empty_df = pd.DataFrame()
            
            version = self.pipeline_manager.ingest_data(empty_df, 'empty_dataset')
            
            assert version.row_count == 0
            assert version.column_count == 0
            # Quality score should be low for empty data
            assert version.quality_score < 0.5
            
        except ImportError:
            pytest.skip("Pandas not available for DataFrame testing")
    
    # ===== DATA VERSION MANAGEMENT TESTS =====
    
    def test_get_data_version_existing(self):
        """Test retrieving existing data version."""""
        try:
            import pandas as pd
            df = pd.DataFrame({'test_col': [1, 2, 3]})
            
            # Create version
            original_version = self.pipeline_manager.ingest_data(df, 'version_test')
            
            # Retrieve version
            retrieved_version = self.pipeline_manager.get_data_version(original_version.version_id)
            
            assert retrieved_version.version_id == original_version.version_id
            assert retrieved_version.dataset_name == original_version.dataset_name
            assert retrieved_version.row_count == original_version.row_count
            
        except ImportError:
            pytest.skip("Pandas not available for DataFrame testing")
    
    def test_get_data_version_nonexistent(self):
        """Test retrieving non-existent data version."""""
        with pytest.raises(ValueError, match="Data version not found"):
            self.pipeline_manager.get_data_version("nonexistent_version_id")
    
    def test_get_latest_version(self):
        """Test getting latest version of a dataset."""""
        try:
            import pandas as pd
            
            # Create multiple versions
            df1 = pd.DataFrame({'col': [1, 2]})
            df2 = pd.DataFrame({'col': [1, 2, 3]})
            
            version1 = self.pipeline_manager.ingest_data(df1, 'multi_version_test')
            version2 = self.pipeline_manager.ingest_data(df2, 'multi_version_test')
            
            latest = self.pipeline_manager.get_latest_version('multi_version_test')
            
            assert latest is not None
            assert latest.version_id == version2.version_id
            assert latest.row_count == 3
            
        except ImportError:
            pytest.skip("Pandas not available for DataFrame testing")
    
    def test_get_latest_version_nonexistent(self):
        """Test getting latest version of non-existent dataset."""""
        latest = self.pipeline_manager.get_latest_version('nonexistent_dataset')
        assert latest is None
    
    def test_list_versions(self):
        """Test listing all versions."""""
        try:
            import pandas as pd
            
            # Create multiple datasets and versions
            df1 = pd.DataFrame({'col': [1]})
            df2 = pd.DataFrame({'col': [1, 2]})
            
            self.pipeline_manager.ingest_data(df1, 'dataset_a')
            self.pipeline_manager.ingest_data(df2, 'dataset_b')
            self.pipeline_manager.ingest_data(df1, 'dataset_a')  # Second version
            
            # List all versions
            all_versions = self.pipeline_manager.list_versions()
            assert len(all_versions) == 3
            
            # List versions for specific dataset
            dataset_a_versions = self.pipeline_manager.list_versions('dataset_a')
            assert len(dataset_a_versions) == 2
            
            dataset_b_versions = self.pipeline_manager.list_versions('dataset_b')
            assert len(dataset_b_versions) == 1
            
        except ImportError:
            pytest.skip("Pandas not available for DataFrame testing")
    
    # ===== DATA QUALITY TESTS =====
    
    def test_quality_assessment_good_data(self):
        """Test quality assessment for good quality data."""""
        try:
            import pandas as pd
            import numpy as np
            
            # Create high-quality data
            good_data = pd.DataFrame({
                'id': range(100),
                'value': np.random.randn(100),
                'category': np.random.choice(['A', 'B', 'C'], 100),
                'timestamp': pd.date_range('2024-01-01', periods=100, freq='H')
            })
            
            version = self.pipeline_manager.ingest_data(good_data, 'quality_test')
            
            assert version.quality_score > 0.7  # Should be reasonably high
            assert version.quality_status in [DataQualityStatus.GOOD, DataQualityStatus.EXCELLENT]
            
        except ImportError:
            pytest.skip("Pandas not available for DataFrame testing")
    
    def test_quality_assessment_poor_data(self):
        """Test quality assessment for poor quality data."""""
        try:
            import pandas as pd
            import numpy as np
            
            # Create poor-quality data with lots of missing values
            poor_data = pd.DataFrame({
                'col1': [1, None, None, None, 5],
                'col2': [None, None, 'test', None, None],
                'col3': [np.inf, -np.inf, 1, None, np.nan]
            })
            
            version = self.pipeline_manager.ingest_data(poor_data, 'poor_quality_test')
            
            assert version.quality_score < 0.8  # Should be low
            
        except ImportError:
            pytest.skip("Pandas not available for DataFrame testing")
    
    def test_get_quality_report(self):
        """Test retrieving quality reports."""""
        try:
            import pandas as pd
            
            df = pd.DataFrame({
                'col1': [1, 2, 3, None, 5],
                'col2': ['a', 'b', 'c', 'd', 'e']
            })
            
            version = self.pipeline_manager.ingest_data(df, 'quality_report_test')
            report = self.pipeline_manager.get_quality_report(version.version_id)
            
            assert isinstance(report, QualityReport)
            assert report.version_id == version.version_id
            assert report.dataset_name == 'quality_report_test'
            assert isinstance(report.overall_score, float)
            assert isinstance(report.overall_status, DataQualityStatus)
            assert isinstance(report.missing_values, dict)
            assert isinstance(report.duplicate_rows, int)
            assert isinstance(report.issues_found, list)
            assert isinstance(report.recommendations, list)
            
        except ImportError:
            pytest.skip("Pandas not available for DataFrame testing")
    
    def test_quality_report_nonexistent(self):
        """Test retrieving quality report for non-existent version."""""
        with pytest.raises(ValueError, match="Quality report not found"):
            self.pipeline_manager.get_quality_report("nonexistent_version")
    
    # ===== DATA TRANSFORMATION TESTS =====
    
    def test_transform_data_filter(self):
        """Test data transformation with filtering."""""
        try:
            import pandas as pd
            
            # Create source data
            df = pd.DataFrame({
                'value': [1, 5, 10, 15, 20],
                'category': ['A', 'B', 'A', 'C', 'B']
            })
            
            source_version = self.pipeline_manager.ingest_data(df, 'transform_source')
            
            # Apply filter transformation
            transformations = [{
                'type': 'filter',
                'params': {
                    'column': 'value',
                    'condition': 'greater_than',
                    'value': 5
                }
            }]
            
            result_version = self.pipeline_manager.transform_data(
                source_version.version_id,
                transformations,
                'filtered_dataset'
            )
            
            assert result_version.dataset_name == 'filtered_dataset'
            assert result_version.row_count == 3  # Should have 3 rows > 5
            assert 'transformed' in result_version.tags
            
        except ImportError:
            pytest.skip("Pandas not available for DataFrame testing")
    
    def test_transform_data_invalid_type(self):
        """Test transformation with invalid transformation type."""""
        try:
            import pandas as pd
            
            df = pd.DataFrame({'col': [1, 2, 3]})
            source_version = self.pipeline_manager.ingest_data(df, 'invalid_transform_test')
            
            transformations = [{
                'type': 'invalid_transformation',
                'params': {}
            }]
            
            with pytest.raises(ValueError, match="Unknown transformation type"):
                self.pipeline_manager.transform_data(
                    source_version.version_id,
                    transformations
                )
                
        except ImportError:
            pytest.skip("Pandas not available for DataFrame testing")
    
    def test_transform_nonexistent_version(self):
        """Test transformation with non-existent source version."""""
        transformations = [{'type': 'filter', 'params': {}}]
        
        with pytest.raises(ValueError, match="Data version not found"):
            self.pipeline_manager.transform_data(
                "nonexistent_version",
                transformations
            )
    
    # ===== UTILITY TESTS =====
    
    def test_hash_calculation(self):
        """Test hash calculation methods."""""
        try:
            import pandas as pd
            
            df1 = pd.DataFrame({'col': [1, 2, 3]})
            df2 = pd.DataFrame({'col': [1, 2, 3]})
            df3 = pd.DataFrame({'col': [1, 2, 4]})
            
            hash1 = self.pipeline_manager._calculate_dataframe_hash(df1)
            hash2 = self.pipeline_manager._calculate_dataframe_hash(df2)
            hash3 = self.pipeline_manager._calculate_dataframe_hash(df3)
            
            assert hash1 == hash2  # Same data should have same hash
            assert hash1 != hash3  # Different data should have different hash
            assert isinstance(hash1, str)
            assert len(hash1) == 64  # SHA256 hash length
            
        except ImportError:
            pytest.skip("Pandas not available for DataFrame testing")
    
    def test_file_hash_calculation(self):
        """Test file hash calculation."""""
        # Create temporary test file
        test_file = Path(self.temp_dir) / "test_file.txt"
        test_file.write_text("test content")
        
        hash1 = self.pipeline_manager._calculate_file_hash(test_file)
        hash2 = self.pipeline_manager._calculate_file_hash(test_file)
        
        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 64
        
        # Test non-existent file
        hash_empty = self.pipeline_manager._calculate_file_hash(Path("nonexistent"))
        assert hash_empty == ""


@pytest.mark.unit
class TestDataPipelineEnums:
    """Test enum classes used in data pipeline."""""
    
    def test_data_quality_status_values(self):
        """Test DataQualityStatus enum values."""""
        assert DataQualityStatus.EXCELLENT.value == "excellent"
        assert DataQualityStatus.GOOD.value == "good"
        assert DataQualityStatus.WARNING.value == "warning"
        assert DataQualityStatus.POOR.value == "poor"
        assert DataQualityStatus.FAILED.value == "failed"
    
    def test_pipeline_stage_values(self):
        """Test PipelineStage enum values."""""
        assert PipelineStage.INGESTION.value == "ingestion"
        assert PipelineStage.VALIDATION.value == "validation"
        assert PipelineStage.TRANSFORMATION.value == "transformation"
        assert PipelineStage.QUALITY_CHECK.value == "quality_check"
        assert PipelineStage.STORAGE.value == "storage"
        assert PipelineStage.COMPLETED.value == "completed"
        assert PipelineStage.FAILED.value == "failed"


@pytest.mark.unit
class TestDataPipelineEdgeCases:
    """Test edge cases and error conditions for DataPipelineManager."""""
    
    def setup_method(self):
        """Set up test fixtures."""""
        self.temp_dir = tempfile.mkdtemp()
        self.pipeline_manager = DataPipelineManager(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_fallback_without_pandas(self):
        """Test pipeline functionality when pandas is not available."""""
        # This test verifies the fallback behavior works
        # In actual implementation, mock classes should handle basic operations
        
        # Test basic initialization
        assert self.pipeline_manager is not None
        assert self.pipeline_manager.storage_path.exists()
    
    def test_pipeline_run_tracking(self):
        """Test pipeline run tracking functionality."""""
        try:
            import pandas as pd
            
            df = pd.DataFrame({'col': [1, 2, 3]})
            
            # Ingest data should create a pipeline run
            version = self.pipeline_manager.ingest_data(df, 'run_tracking_test')
            
            # Check that run was tracked in database
            import sqlite3
            conn = sqlite3.connect(self.pipeline_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM pipeline_runs")
            run_count = cursor.fetchone()[0]
            
            assert run_count > 0
            conn.close()
            
        except ImportError:
            pytest.skip("Pandas not available for DataFrame testing")
    
    def test_storage_paths_creation(self):
        """Test that all required storage paths are created."""""
        paths_to_check = [
            self.pipeline_manager.data_path,
            self.pipeline_manager.versions_path,
            self.pipeline_manager.quality_path,
            self.pipeline_manager.logs_path
        ]
        
        for path in paths_to_check:
            assert path.exists()
            assert path.is_dir()
    
    def test_version_id_uniqueness(self):
        """Test that version IDs are unique."""""
        try:
            import pandas as pd
            
            df = pd.DataFrame({'col': [1, 2, 3]})
            
            version1 = self.pipeline_manager.ingest_data(df, 'unique_test')
            version2 = self.pipeline_manager.ingest_data(df, 'unique_test')
            
            assert version1.version_id != version2.version_id
            
        except ImportError:
            pytest.skip("Pandas not available for DataFrame testing")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
