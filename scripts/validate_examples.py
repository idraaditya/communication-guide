#!/usr/bin/env python3
"""
Validate ESP32 Examples Compile
Tests all PlatformIO and ESP-IDF examples in the examples/ directory.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict
from dataclasses import dataclass
from collections import defaultdict

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

@dataclass
class ValidationResult:
    example: str
    build_system: str  # "platformio" or "espidf"
    success: bool
    error: str = ""
    duration: float = 0.0

class ExampleValidator:
    def __init__(self, examples_dir: Path = EXAMPLES_DIR):
        self.examples_dir = examples_dir
        self.results: List[ValidationResult] = []
    
    def detect_build_system(self, example_dir: Path) -> str:
        """Detect if PlatformIO or ESP-IDF project."""
        if (example_dir / "platformio.ini").exists():
            return "platformio"
        elif (example_dir / "CMakeLists.txt").exists() and (example_dir / "main").exists():
            return "espidf"
        return "unknown"
    
    def validate_platformio(self, example_dir: Path) -> Tuple[bool, str]:
        """Validate PlatformIO project compiles."""
        try:
            # Check platformio.ini exists
            if not (example_dir / "platformio.ini").exists():
                return False, "No platformio.ini found"
            
            # Run pio check (syntax check)
            result = subprocess.run(
                ["pio", "check", "-d", str(example_dir)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                return False, f"pio check failed: {result.stderr}"
            
            # Run pio run (build)
            result = subprocess.run(
                ["pio", "run", "-d", str(example_dir)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                return False, f"pio run failed: {result.stderr}"
            
            return True, "Success"
            
        except subprocess.TimeoutExpired:
            return False, "Build timeout"
        except FileNotFoundError:
            return False, "PlatformIO not installed"
        except Exception as e:
            return False, str(e)
    
    def validate_espidf(self, example_dir: Path) -> Tuple[bool, str]:
        """Validate ESP-IDF project compiles."""
        try:
            # Check for ESP-IDF environment
            idf_path = Path("/opt/esp/idf") if Path("/opt/esp/idf").exists() else None
            if not idf_path:
                # Try common locations
                for p in ["/home/esp/esp-idf", "/opt/esp-idf", "/usr/local/esp-idf"]:
                    if Path(p).exists():
                        idf_path = Path(p)
                        break
            
            if not idf_path:
                return False, "ESP-IDF not found"
            
            # Source ESP-IDF environment and build
            build_script = f"""
            source {idf_path}/export.sh
            cd {example_dir}
            idf.py build
            """
            
            result = subprocess.run(
                ["bash", "-c", build_script],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                return False, f"idf.py build failed: {result.stderr}"
            
            return True, "Success"
            
        except subprocess.TimeoutExpired:
            return False, "Build timeout"
        except Exception as e:
            return False, str(e)
    
    def validate_all(self) -> Dict[str, List[ValidationResult]]:
        """Validate all examples in the examples directory."""
        results_by_type = defaultdict(list)
        
        if not self.examples_dir.exists():
            print(f"Examples directory not found: {self.examples_dir}")
            return results_by_type
        
        examples = [d for d in self.examples_dir.iterdir() if d.is_dir()]
        print(f"Found {len(examples)} example directories")
        
        for example_dir in examples:
            build_system = self.detect_build_system(example_dir)
            print(f"\nValidating {example_dir.name} ({build_system})...")
            
            import time
            start = time.time()
            
            if build_system == "platformio":
                success, error = self.validate_platformio(example_dir)
            elif build_system == "espidf":
                success, error = self.validate_espidf(example_dir)
            else:
                success, error = False, f"Unknown build system: {build_system}"
            
            duration = time.time() - start
            result = ValidationResult(
                example=example_dir.name,
                build_system=build_system,
                success=success,
                error=error,
                duration=duration
            )
            
            results_by_type[build_system].append(result)
            
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"  {status} ({duration:.1f}s)")
            if not success:
                print(f"  Error: {error}")
        
        return results_by_type
    
    def print_summary(self, results: Dict[str, List[ValidationResult]]):
        """Print validation summary."""
        total = sum(len(r) for r in results.values())
        passed = sum(sum(1 for r in lst if r.success) for lst in results.values())
        failed = total - passed
        
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
        
        for build_type, type_results in results.items():
            type_passed = sum(1 for r in type_results if r.success)
            type_total = len(type_results)
            print(f"\n{build_type.upper()}: {type_passed}/{type_total} passed")
            
            for result in type_results:
                status = "✓" if result.success else "✗"
                print(f"  {status} {result.example} ({result.duration:.1f}s)")
                if not result.success:
                    print(f"    Error: {result.error}")
        
        if failed > 0:
            print("\n❌ Some validations failed!")
            sys.exit(1)
        else:
            print("\n✅ All validations passed!")

def main():
    import argparse
    from collections import defaultdict
    
    parser = argparse.ArgumentParser(description="Validate ESP32 examples compile")
    parser.add_argument("--examples-dir", type=Path, default=EXAMPLES_DIR,
                       help="Path to examples directory")
    parser.add_argument("--only", choices=["platformio", "espidf"], 
                       help="Only validate specific build system")
    args = parser.parse_args()
    
    validator = ExampleValidator(args.examples_dir)
    results = validator.validate_all()
    
    if args.only:
        results = {args.only: results.get(args.only, [])}
    
    validator.print_summary(results)

if __name__ == '__main__':
    main()