"""
Pandoc Converter Utility - Converts markdown to PowerPoint using company templates
"""
import subprocess
import tempfile
import os
import base64
from pathlib import Path
from typing import Optional

class PandocConverter:
    """Handles markdown to PowerPoint conversion using Pandoc"""
    
    def __init__(self, template_path: Optional[str] = None):
        self.template_path = template_path or self._get_default_template_path()
        self._validate_setup()
    
    def _get_default_template_path(self) -> str:
        """Get default template path"""
        current_dir = Path(__file__).parent.parent
        template_path = current_dir / "templates" / "company_template.pptx"
        return str(template_path)
    
    def _validate_setup(self):
        """Validate that Pandoc is available and template exists"""
        # Check if Pandoc is available
        try:
            result = subprocess.run(['pandoc', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise RuntimeError("Pandoc is not available or not working properly")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise RuntimeError(f"Pandoc validation failed: {str(e)}")
        
        # Check if template exists (optional - will work without template)
        if self.template_path and not os.path.exists(self.template_path):
            print(f"Warning: Template not found at {self.template_path}. Will use Pandoc default.")
            self.template_path = None
    
    def markdown_to_pptx(self, markdown_content: str, output_filename: str = None) -> bytes:
        """
        Convert markdown content to PowerPoint presentation
        
        Args:
            markdown_content: The markdown content to convert
            output_filename: Optional custom filename for debugging
            
        Returns:
            bytes: The PowerPoint file as bytes
        """
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as md_file:
                md_file.write(markdown_content)
                md_file.flush()
                
                with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as pptx_file:
                    # Build Pandoc command
                    pandoc_cmd = [
                        'pandoc',
                        md_file.name,
                        '-o', pptx_file.name,
                        '-t', 'pptx'
                    ]
                    
                    # Add template if available
                    if self.template_path and os.path.exists(self.template_path):
                        pandoc_cmd.extend(['--reference-doc', self.template_path])
                        print(f"Using template: {self.template_path}")
                    else:
                        print("Using Pandoc default template (no custom template)")
                    
                    # Add additional Pandoc options for better PowerPoint generation
                    pandoc_cmd.extend([
                        '--slide-level=2',  # Level 2 headers (##) create new slides
                        '--wrap=preserve'   # Preserve line wrapping from markdown
                    ])
                    
                    print(f"Running Pandoc command: {' '.join(pandoc_cmd)}")
                    
                    # Execute Pandoc conversion
                    result = subprocess.run(
                        pandoc_cmd,
                        capture_output=True,
                        text=True,
                        timeout=60  # 60 second timeout
                    )
                    
                    if result.returncode != 0:
                        error_msg = f"Pandoc conversion failed (exit code {result.returncode})"
                        if result.stderr:
                            error_msg += f": {result.stderr}"
                        if result.stdout:
                            error_msg += f". Output: {result.stdout}"
                        raise RuntimeError(error_msg)
                    
                    # Read the generated PowerPoint file
                    with open(pptx_file.name, 'rb') as f:
                        pptx_bytes = f.read()
                    
                    print(f"Successfully converted markdown to PowerPoint. Size: {len(pptx_bytes)} bytes")
                    
                    # Optional: Save debug copy
                    if output_filename:
                        debug_path = f"/tmp/{output_filename}"
                        try:
                            with open(debug_path, 'wb') as debug_file:
                                debug_file.write(pptx_bytes)
                            print(f"Debug copy saved to: {debug_path}")
                        except Exception as e:
                            print(f"Could not save debug copy: {e}")
                    
                    return pptx_bytes
                    
        except subprocess.TimeoutExpired:
            raise RuntimeError("Pandoc conversion timed out after 60 seconds")
        except Exception as e:
            raise RuntimeError(f"PowerPoint generation failed: {str(e)}")
        finally:
            # Clean up temporary files
            try:
                if 'md_file' in locals():
                    os.unlink(md_file.name)
                if 'pptx_file' in locals():
                    os.unlink(pptx_file.name)
            except Exception as e:
                print(f"Warning: Could not clean up temporary files: {e}")
    
    def markdown_to_pptx_base64(self, markdown_content: str, output_filename: str = None) -> str:
        """
        Convert markdown to PowerPoint and return as base64 string
        
        Args:
            markdown_content: The markdown content to convert
            output_filename: Optional custom filename for debugging
            
        Returns:
            str: Base64 encoded PowerPoint file
        """
        pptx_bytes = self.markdown_to_pptx(markdown_content, output_filename)
        return base64.b64encode(pptx_bytes).decode('utf-8')
    
    def validate_markdown(self, markdown_content: str) -> dict:
        """
        Validate markdown content before conversion
        
        Args:
            markdown_content: The markdown content to validate
            
        Returns:
            dict: Validation results
        """
        validation = {
            'is_valid': True,
            'warnings': [],
            'slide_count': 0,
            'has_yaml_header': False,
            'has_tables': False
        }
        
        lines = markdown_content.split('\n')
        
        # Check for YAML front matter
        if lines and lines[0].strip() == '---':
            validation['has_yaml_header'] = True
        else:
            validation['warnings'].append("No YAML front matter found")
        
        # Count slides (## headers)
        slide_count = 0
        for line in lines:
            if line.strip().startswith('## '):
                slide_count += 1
        
        validation['slide_count'] = slide_count
        
        if slide_count == 0:
            validation['warnings'].append("No slides detected (no ## headers found)")
        elif slide_count > 20:
            validation['warnings'].append(f"High slide count ({slide_count}) may cause performance issues")
        
        # Check for tables
        for line in lines:
            if '|' in line and line.count('|') >= 2:
                validation['has_tables'] = True
                break
        
        # Check for basic content
        content_lines = [line for line in lines if line.strip() and not line.startswith(('#', '---', '::'))]
        if len(content_lines) < 3:
            validation['warnings'].append("Very little content found")
            validation['is_valid'] = False
        
        return validation
    
    def get_template_info(self) -> dict:
        """Get information about the current template"""
        return {
            'template_path': self.template_path,
            'template_exists': self.template_path and os.path.exists(self.template_path),
            'pandoc_available': self._check_pandoc_available()
        }
    
    def _check_pandoc_available(self) -> bool:
        """Check if Pandoc is available"""
        try:
            result = subprocess.run(['pandoc', '--version'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False