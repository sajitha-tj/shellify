import pkg_resources
import subprocess
from pathlib import Path

_REQUIREMENTS_PATH = Path(__file__).parent.with_name('requirements.txt')

class TestRequirements:
    def test_requirements(self):
        requirements = pkg_resources.parse_requirements(_REQUIREMENTS_PATH.open())
        try:
            for requirement in requirements:
                requirement = str(requirement)
                assert pkg_resources.require(requirement)
        except Exception as e:
            return False, e
        return True, None
    
    def test_ffmpeg(self):
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            return False, 'ffmpeg is not installed.'
        return True, None