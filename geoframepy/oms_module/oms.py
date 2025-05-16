"""
OMS Runner Library - A Python library for running OMS3 simulations.

This library provides functions for automatically detecting Java JDK 11,
setting up OMS3 projects, and running simulations on Windows, macOS, and Linux.

Original Authors: Martin Morlot, Riccardo Rigon, Giuseppe Formetta
Enhanced by: Riccardo Rigon, [Your Name]

Distributed under GPL 3.0
"""

import os
import sys
import subprocess
import platform
import json
import datetime
import traceback
from pathlib import Path

# Global variables to store OMS configuration and logs
oms_config = None
oms_logs = {
    "warnings": [],
    "errors": [],
    "info": [],
    "execution_history": []
}

def log_message(level, message):
    """Add a message to the log storage.
    
    Args:
        level: The log level ("info", "warning", or "error")
        message: The message to log
    """
    global oms_logs
    
    # Ensure the level exists in the logs dictionary
    if level not in oms_logs:
        oms_logs[level] = []
    
    # Add the message to the appropriate log level
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    oms_logs[level].append(f"[{timestamp}] {message}")
    
    # Always print errors immediately
    if level == "error":
        print(f"❌ Error: {message}")

def find_java_jdk11():
    """Detect Java JDK 11 installation on the current platform.
    
    Returns:
        str: Path to Java executable if found, None otherwise
    """
    # Delegate to the appropriate platform-specific function
    if platform.system() == 'Windows':
        return find_java_jdk11_windows()
    elif platform.system() == 'Darwin':  # macOS
        return find_java_jdk11_mac()
    elif platform.system() == 'Linux':
        return find_java_jdk11_linux()
    else:
        print(f"Unsupported platform: {platform.system()}")
        return None

def find_java_jdk11_windows():
    """Function to automatically detect Java JDK 11 installation on Windows.
    Returns the path to java executable if found, None otherwise."""
    java_path = None
    
    # Method 1: Check Windows Registry for JDK installations
    try:
        import winreg
        # Open the registry key that contains JDK installations
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\JDK") as jdk_key:
            # Iterate through the subkeys to find Java 11
            i = 0
            while True:
                try:
                    version_key_name = winreg.EnumKey(jdk_key, i)
                    if version_key_name.startswith('11.'):
                        with winreg.OpenKey(jdk_key, version_key_name) as version_key:
                            java_home, _ = winreg.QueryValueEx(version_key, "JavaHome")
                            java_bin = os.path.join(java_home, "bin", "java.exe")
                            if os.path.exists(java_bin):
                                print(f"Found Java 11 in Windows Registry: {java_bin}")
                                return java_bin
                    i += 1
                except WindowsError:
                    break
    except Exception as e:
        print(f"Registry check failed: {e}")
    
    # Method 2: Check standard installation locations
    java_dirs = [
        "C:\\Program Files\\Java\\",
        "C:\\Program Files (x86)\\Java\\",
        os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Java'),
        os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'Java'),
        os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'AdoptOpenJDK'),
        os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Eclipse Adoptium')
    ]
    
    for java_dir in java_dirs:
        if not os.path.exists(java_dir):
            continue
            
        for jdk_dir in os.listdir(java_dir):
            if '11' in jdk_dir and ('jdk' in jdk_dir.lower() or 'openjdk' in jdk_dir.lower()):
                candidate = os.path.join(java_dir, jdk_dir, 'bin', 'java.exe')
                    
                if os.path.exists(candidate):
                    print(f"Found Java 11 in standard location: {candidate}")
                    return candidate
    
    # Method 3: Check JAVA_HOME environment variable
    java_home = os.environ.get('JAVA_HOME')
    if java_home:
        candidate = os.path.join(java_home, 'bin', 'java.exe')
        if os.path.exists(candidate):
            # Verify it's Java 11
            try:
                result = subprocess.run([candidate, '-version'], 
                                     capture_output=True, text=True, check=False)
                if '11' in result.stderr:  # java -version outputs to stderr
                    print(f"Found Java 11 via JAVA_HOME: {candidate}")
                    return candidate
            except Exception as e:
                print(f"JAVA_HOME check failed: {e}")
    
    # Method 4: Check conda environments if conda is available
    try:
        # List conda environments
        result = subprocess.run(['conda', 'env', 'list', '--json'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            env_data = json.loads(result.stdout)
            for env_path in env_data.get('envs', []):
                # Check if this env has Java 11
                java_in_env = os.path.join(env_path, 'Library', 'bin', 'java.exe')
                if os.path.exists(java_in_env):
                    # Verify version is 11
                    try:
                        ver_check = subprocess.run([java_in_env, '-version'], 
                                                 capture_output=True, text=True, check=False)
                        if '11' in ver_check.stderr:  # java -version outputs to stderr
                            print(f"Found Java 11 in conda environment: {java_in_env}")
                            return java_in_env
                    except Exception:
                        pass
    except Exception as e:
        print(f"Conda check failed: {e}")
    
    # Method 5: Check the PATH for java.exe and verify version
    try:
        result = subprocess.run(['where', 'java'], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            java_paths = result.stdout.strip().split('\r\n')
            for path in java_paths:
                try:
                    ver_check = subprocess.run([path, '-version'], 
                                             capture_output=True, text=True, check=False)
                    if '11' in ver_check.stderr:  # java -version outputs to stderr
                        print(f"Found Java 11 in PATH: {path}")
                        return path
                except Exception:
                    pass
    except Exception as e:
        print(f"PATH check failed: {e}")
    
    # No Java 11 found
    print("⚠️ No Java JDK 11 installation found automatically on Windows.")
    print("Please set the 'java_jdk11_path' variable manually.")
    
    return java_path

def find_java_jdk11_mac():
    """Function to automatically detect Java JDK 11 installation on macOS.
    Returns the path to java executable if found, None otherwise."""
    java_path = None
    
    # Method 1: Use /usr/libexec/java_home to find JDK installations (macOS specific)
    try:
        result = subprocess.run(['/usr/libexec/java_home', '-v', '11'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            java_home = result.stdout.strip()
            java_path = os.path.join(java_home, 'bin', 'java')
            print(f"Found Java 11 using /usr/libexec/java_home: {java_path}")
            return java_path
    except Exception as e:
        print(f"java_home method failed: {e}")
    
    # Method 2: Check standard installation locations
    java_dirs = [
        "/Library/Java/JavaVirtualMachines/",  # macOS standard location
        os.path.expanduser("~/Library/Java/JavaVirtualMachines/")  # macOS user location
    ]
    
    for java_dir in java_dirs:
        if not os.path.exists(java_dir):
            continue
            
        for jdk_dir in os.listdir(java_dir):
            if '11' in jdk_dir:  # Simple check for Java 11
                candidate = os.path.join(java_dir, jdk_dir, 'Contents', 'Home', 'bin', 'java')
                    
                if os.path.exists(candidate) and os.access(candidate, os.X_OK):
                    print(f"Found Java 11 in standard location: {candidate}")
                    return candidate
    
    # Method 3: Check if JDK is installed through Homebrew (macOS)
    try:
        result = subprocess.run(['brew', '--prefix', 'openjdk@11'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            brew_path = result.stdout.strip()
            java_path = os.path.join(brew_path, 'bin', 'java')
            if os.path.exists(java_path):
                print(f"Found Java 11 installed via Homebrew: {java_path}")
                return java_path
    except Exception as e:
        print(f"Homebrew check failed: {e}")
    
    # No Java 11 found
    print("⚠️ No Java JDK 11 installation found automatically on macOS.")
    print("Please set the 'java_jdk11_path' variable manually.")
    
    return java_path

def find_java_jdk11_linux():
    """Function to automatically detect Java JDK 11 installation on Linux.
    Returns the path to java executable if found, None otherwise."""
    java_path = None
    
    # Method 1: Check standard Linux installation locations
    java_dirs = [
        "/usr/lib/jvm/",
        "/opt/java/",
        "/usr/java/",
        os.path.expanduser("~/.sdkman/candidates/java/")
    ]
    
    for java_dir in java_dirs:
        if not os.path.exists(java_dir):
            continue
            
        for jdk_dir in os.listdir(java_dir):
            if '11' in jdk_dir and os.path.isdir(os.path.join(java_dir, jdk_dir)):
                candidate = os.path.join(java_dir, jdk_dir, 'bin', 'java')
                if os.path.exists(candidate) and os.access(candidate, os.X_OK):
                    # Verify it's Java 11
                    try:
                        result = subprocess.run([candidate, '-version'], 
                                             capture_output=True, text=True, check=False)
                        if '11' in result.stderr:  # java -version outputs to stderr
                            print(f"Found Java 11 in standard location: {candidate}")
                            return candidate
                    except Exception:
                        pass
    
    # Method 2: Check alternatives system
    try:
        result = subprocess.run(['update-alternatives', '--list', 'java'], 
                             capture_output=True, text=True, check=False)
        if result.returncode == 0:
            java_paths = result.stdout.strip().split('\n')
            for path in java_paths:
                try:
                    ver_check = subprocess.run([path, '-version'], 
                                            capture_output=True, text=True, check=False)
                    if '11' in ver_check.stderr:  # java -version outputs to stderr
                        print(f"Found Java 11 via alternatives: {path}")
                        return path
                except Exception:
                    pass
    except Exception as e:
        print(f"Alternatives check failed: {e}")
    
    # Method 3: Check JAVA_HOME environment variable
    java_home = os.environ.get('JAVA_HOME')
    if java_home:
        candidate = os.path.join(java_home, 'bin', 'java')
        if os.path.exists(candidate) and os.access(candidate, os.X_OK):
            # Verify it's Java 11
            try:
                result = subprocess.run([candidate, '-version'], 
                                      capture_output=True, text=True, check=False)
                if '11' in result.stderr:  # java -version outputs to stderr
                    print(f"Found Java 11 via JAVA_HOME: {candidate}")
                    return candidate
            except Exception as e:
                print(f"JAVA_HOME check failed: {e}")
    
    # No Java 11 found
    print("⚠️ No Java JDK 11 installation found automatically on Linux.")
    print("Please set the 'java_jdk11_path' variable manually.")
    
    return java_path

def verify_java_version(java_path):
    """Verify that the provided path is Java 11.
    
    Args:
        java_path: Path to Java executable
        
    Returns:
        bool: True if Java 11, False otherwise
    """
    if not java_path or not os.path.exists(java_path):
        return False
    
    try:
        result = subprocess.run([java_path, '-version'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0 and '11' in result.stderr:  # java -version outputs to stderr
            return True
        else:
            return False
    except Exception:
        return False

def setup_OMS_project(java_path, proj_location, console_location, verbose=True):
    """Set up an OMS project with all necessary configurations.
    
    This function validates paths and stores configuration globally for reuse.
    
    Args:
        java_path: Path to Java JDK 11 executable
        proj_location: Path to the OMS project folder
        console_location: Path to the OMS console folder
        verbose: Whether to print informational messages (default: True)
        
    Returns:
        bool: True if setup was successful, False otherwise
    """
    global oms_config, oms_logs
    
    # Reset logs for a fresh setup
    oms_logs = {
        "warnings": [],
        "errors": [],
        "info": [],
        "execution_history": []
    }
    
    # Normalize paths for the current platform
    proj_location = os.path.normpath(proj_location)
    console_location = os.path.normpath(console_location)
    
    # Verify Java path exists
    if not os.path.exists(java_path):
        log_message("error", f"Java path {java_path} does not exist")
        return False
    
    # Verify Java version is 11
    if not verify_java_version(java_path):
        log_message("error", f"Java at {java_path} is not version 11")
        return False
    
    # Verify console location exists
    if not os.path.exists(console_location):
        log_message("error", f"Console location {console_location} does not exist")
        return False
    
    # Verify project location exists
    if not os.path.exists(proj_location):
        log_message("error", f"Project location {proj_location} does not exist")
        return False
    
    # Save the original directory
    original_dir = os.getcwd()
    
    # Store configuration in global variable for reuse
    oms_config = {
        "java_path": java_path,
        "proj_location": proj_location,
        "console_location": console_location,
        "original_dir": original_dir,
        "verbose": verbose,
        "platform": platform.system()
    }
    
    # Log successful setup
    log_message("info", "OMS project setup completed successfully")
    
    if verbose:
        print(f"✅ OMS project setup complete:")
        print(f"   - Java: {java_path}")
        print(f"   - Project: {proj_location}")
        print(f"   - Console: {console_location}")
        print(f"   - Platform: {platform.system()}")
    
    return True

def run_simulation(simulation_path, verbose=None):
    """Run an OMS simulation using the global configuration.
    
    Args:
        simulation_path: Path to the simulation file (relative to project location)
        verbose: Whether to print warnings and information (default: None, uses setup value)
        
    Returns:
        bool: True if simulation ran successfully, False otherwise
    """
    global oms_config, oms_logs
    
    # Check if OMS project is configured
    if not oms_config:
        log_message("error", "Cannot run simulation: OMS project not configured")
        print("   Please run setup_OMS_project first")
        return False
    
    # Get configuration values
    java_path = oms_config["java_path"]
    proj_location = oms_config["proj_location"]
    console_location = oms_config["console_location"]
    platform_name = oms_config["platform"]
    
    # Use setup's verbose setting if not specified
    if verbose is None:
        verbose = oms_config.get("verbose", True)
    
    # Save current directory and change to project directory
    current_dir = os.getcwd()
    os.chdir(proj_location)
    
    try:
        # Build the command based on platform
        if platform_name == 'Windows':
            # Windows uses semicolons instead of colons for classpath separation
            classpath = f".;{console_location}\\*;lib\\*;dist\\*"
            cmd = [
                java_path,
                f"-Doms3.work={proj_location}",
                "-cp", classpath,
                "oms3.CLI",
                "-r", simulation_path
            ]
        else:  # macOS or Linux
            # Unix platforms use colons for classpath separation
            classpath = f".:{console_location}/*:lib/*:dist/*"
            cmd = [
                java_path,
                f"-Doms3.work={proj_location}",
                "-cp", classpath,
                "oms3.CLI",
                "-r", simulation_path
            ]
        
        # Record in execution history
        history_entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "simulation": simulation_path,
            "command": " ".join(cmd),
            "status": "pending"
        }
        oms_logs["execution_history"].append(history_entry)
        
        # Print command info if verbose
        if verbose:
            print(f"\n🔄 Running simulation: {simulation_path}")
            print("Command:\n" + " ".join(cmd))
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Update execution history
        history_entry["status"] = "success"
        
        # Log success information
        log_message("info", f"Simulation {simulation_path} completed successfully")
        
        # Handle warnings from stderr
        if result.stderr:
            warning_lines = result.stderr.strip().split('\n')
            for line in warning_lines:
                if line.strip():
                    log_message("warning", f"[{simulation_path}] {line}")
            
            # Only print warnings if verbose
            if verbose and warning_lines:
                print("\nWarnings:")
                for line in warning_lines:
                    if line.strip():
                        print(line)
        
        # Print output if verbose
        if verbose:
            print("\n✅ Simulation completed successfully")
            print("\nOutput:")
            print(result.stdout)
        
        return True
    except subprocess.CalledProcessError as e:
        # Update execution history
        history_entry["status"] = "failed"
        
        # Log error information
        error_message = f"Error running simulation {simulation_path}: {e}"
        log_message("error", error_message)
        
        # Log stdout and stderr
        if e.stdout:
            log_message("info", f"Process stdout: {e.stdout}")
        if e.stderr:
            log_message("error", f"Process stderr: {e.stderr}")
        
        # Only print additional details if verbose
        if verbose:
            print(f"\nStdout: {e.stdout}")
            print(f"\nStderr: {e.stderr}")
        
        return False
    except Exception as e:
        # Handle other exceptions
        log_message("error", f"Unexpected error: {str(e)}")
        log_message("error", traceback.format_exc())
        
        if verbose:
            print(f"\nUnexpected error: {str(e)}")
            print(traceback.format_exc())
        
        return False
    finally:
        # Always return to the original directory
        os.chdir(current_dir)

def show_logs(log_type=None, limit=None, clear=False):
    """Display logs collected during setup and execution.
    
    Args:
        log_type: Type of logs to show ("info", "warning", "error", "execution_history", or None for all)
        limit: Maximum number of logs to show (None for all)
        clear: Whether to clear the logs after showing them
        
    Returns:
        None
    """
    global oms_logs
    
    # Check if log type is valid
    if log_type is not None and log_type not in oms_logs:
        print(f"Unknown log type: {log_type}")
        print(f"Available types: {', '.join(oms_logs.keys())}")
        return
    
    # Determine which log types to show
    if log_type:
        log_types = [log_type]
    else:
        log_types = list(oms_logs.keys())
    
    # Display logs for each selected type
    for lt in log_types:
        logs = oms_logs[lt]
        
        # Skip if no logs of this type
        if not logs:
            continue
        
        # Apply limit if specified
        if limit is not None:
            logs = logs[-limit:]
        
        # Print header
        print(f"\n{lt.upper()} LOGS ({len(logs)} entries):")
        print("-" * 50)
        
        # Special formatting for execution history
        if lt == "execution_history":
            for i, entry in enumerate(logs, 1):
                status_icon = "✅" if entry.get("status") == "success" else "❌" if entry.get("status") == "failed" else "⏳"
                print(f"{i}. {status_icon} [{entry['timestamp']}] {entry['simulation']}")
        else:
            # Standard formatting for other logs
            for i, msg in enumerate(logs, 1):
                print(f"{i}. {msg}")
    
    # Clear logs if requested
    if clear:
        for lt in log_types:
            oms_logs[lt] = []

def cleanup_environment():
    """Clean up the environment after running OMS simulations."""
    global oms_config, oms_logs
    
    # Return to original directory if needed
    if oms_config and "original_dir" in oms_config:
        if os.getcwd() != oms_config["original_dir"]:
            os.chdir(oms_config["original_dir"])
            print(f"Returned to original directory: {oms_config['original_dir']}")
    
    # Reset configuration and logs
    oms_config = None
    oms_logs = {
        "warnings": [],
        "errors": [],
        "info": [],
        "execution_history": []
    }
    
    print("Environment cleaned up successfully")

def diagnose_issues():
    """Diagnose common issues that might affect OMS execution."""
    global oms_config
    
    if not oms_config:
        print("No OMS configuration available. Please run setup_OMS_project first.")
        return
    
    platform_name = oms_config["platform"]
    java_path = oms_config["java_path"]
    proj_location = oms_config["proj_location"]
    console_location = oms_config["console_location"]
    
    print(f"OMS Environment Diagnostics for {platform_name}\n" + "-"*40)
    
    # Check Java version
    print("\n1. Checking Java installation:")
    try:
        java_version = subprocess.run([java_path, '-version'], 
                                    capture_output=True, text=True, check=False)
        print(f"   Java version output: {java_version.stderr.strip()}")
        if '11' not in java_version.stderr:
            print("   ⚠️ Warning: This does not appear to be Java 11, which is required for OMS")
    except Exception as e:
        print(f"   ❌ Error checking Java: {e}")
    
    # Check for spaces in paths
    print("\n2. Checking for spaces in paths:")
    if ' ' in java_path:
        print(f"   ⚠️ Java path contains spaces: {java_path}")
        print("   This is handled, but be aware it could cause issues in some contexts")
    if ' ' in proj_location:
        print(f"   ⚠️ Project path contains spaces: {proj_location}")
        print("   This is handled, but be aware it could cause issues in some contexts")
    if ' ' in console_location:
        print(f"   ⚠️ Console path contains spaces: {console_location}")
        print("   This is handled, but be aware it could cause issues in some contexts")
    
    # Platform-specific checks
    if platform_name == "Windows":
        # Windows path length check
        print("\n3. Checking path lengths:")
        print(f"   Project path length: {len(proj_location)} characters")
        if len(proj_location) > 250:
            print("   ⚠️ Warning: Path is approaching Windows 260 character limit")
            print("   This may cause issues. Consider using shorter paths or enabling long path support.")
        
        # Windows-specific advice
        print("\n4. Windows-specific advice:")
        print("   - Use semicolons ; not colons : in classpaths")
        print("   - If Java gives 'Error: Could not find or load main class', check classpath formatting")
        print("   - For 'Access is denied' errors, run as administrator or check folder permissions")
    
    elif platform_name == "Darwin":  # macOS
        # macOS specific checks
        print("\n3. macOS-specific checks:")
        print("   - Ensure JDK 11 is properly installed using Homebrew or the official installer")
        print("   - Check macOS security settings if you get permission issues")
    
    elif platform_name == "Linux":
        # Linux specific checks
        print("\n3. Linux-specific checks:")
        print("   - Check file permissions on the Java executable and project files")
        print("   - Ensure you have the correct JAVA_HOME environment variable set")
    
    # Check for common OMS directory structure
    print("\n4. Checking OMS project structure:")
    expected_dirs = ["dist", "lib", "simulation"]
    for d in expected_dirs:
        path = os.path.join(proj_location, d)
        if os.path.exists(path):
            print(f"   ✅ Found {d} directory")
        else:
            print(f"   ❌ Missing {d} directory, which might be required")