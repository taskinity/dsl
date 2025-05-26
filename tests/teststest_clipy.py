"""
Tests for CLI functionality
"""
import pytest
import tempfile
import os
from click.testing import CliRunner
from dialogchain.cli import cli

class TestCLI:
    
    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Camel Router' in result.output
    
    def test_init_command(self):
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'test_routes.yaml')
            result = runner.invoke(cli, ['init', '--template', 'camera', '--output', output_file])
            
            assert result.exit_code == 0
            assert os.path.exists(output_file)
            
            # Check file content
            with open(output_file, 'r') as f:
                content = f.read()
                assert 'routes:' in content
                assert 'camera' in content.lower()
    
    def test_validate_command(self):
        runner = CliRunner()
        
        # Create a temporary valid config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
routes:
  - name: "test_route"
    from: "timer://5s"
    to: "log://test.log"
""")
            config_file = f.name
        
        try:
            result = runner.invoke(cli, ['validate', '--config', config_file])
            assert result.exit_code == 0
            assert 'valid' in result.output.lower()
        finally:
            os.unlink(config_file)
    
    def test_validate_invalid_config(self):
        runner = CliRunner()
        
        # Create a temporary invalid config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
invalid_yaml: [
""")
            config_file = f.name
        
        try:
            result = runner.invoke(cli, ['validate', '--config', config_file])
            assert result.exit_code != 0
        finally:
            os.unlink(config_file)
    
    def test_run_dry_run(self):
        runner = CliRunner()
        
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
routes:
  - name: "test_route"
    from: "timer://5s"
    processors:
      - type: "transform"
        template: "Hello World"
    to: "log://test.log"
""")
            config_file = f.name
        
        try:
            result = runner.invoke(cli, ['run', '--config', config_file, '--dry-run'])
            assert result.exit_code == 0
            assert 'DRY RUN' in result.output
        finally:
            os.unlink(config_file)

@pytest.mark.integration
class TestCLIIntegration:
    
    def test_full_workflow(self):
        """Test complete CLI workflow: init -> validate -> dry-run"""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, 'workflow_test.yaml')
            
            # Step 1: Initialize configuration
            result = runner.invoke(cli, ['init', '--template', 'camera', '--output', config_file])
            assert result.exit_code == 0
            
            # Step 2: Validate configuration
            result = runner.invoke(cli, ['validate', '--config', config_file])
            assert result.exit_code == 0
            
            # Step 3: Dry run
            result = runner.invoke(cli, ['run', '--config', config_file, '--dry-run'])
            assert result.exit_code == 0