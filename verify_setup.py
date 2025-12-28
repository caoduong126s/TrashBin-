# verify_setup.py

import sys
import subprocess

def check_python_version():
    """Check Python version >= 3.9"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 9:
        print("Python version OK")
        return True
    else:
        print(" Python version too old. Need >= 3.9")
        return False

def check_packages():
    """Check if required packages are installed"""
    required_packages = [
        'tensorflow',
        'numpy',
        'pandas',
        'matplotlib',
        'opencv-python',
        'albumentations',
        'streamlit'
    ]
    
    all_ok = True
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f" {package} installed")
        except ImportError:
            print(f" {package} NOT installed")
            all_ok = False
    
    return all_ok

def check_gpu():
    """Check if GPU is available"""
    try:
        import tensorflow as tf
        gpus = tf.config.list_physical_devices('GPU')
        
        if gpus:
            print(f" GPU available: {len(gpus)} device(s)")
            for gpu in gpus:
                print(f"   - {gpu}")
            return True
        else:
            print(" No GPU detected. Training will use CPU (slower)")
            return False
    except Exception as e:
        print(f" Error checking GPU: {e}")
        return False

def check_directory_structure():
    """Check if directory structure is correct"""
    import os
    
    required_dirs = [
        'data', 'data/raw', 'data/vietnam',
        'notebooks', 'src', 'models', 'outputs', 'demo'
    ]
    
    all_ok = True
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f" {dir_path}/ exists")
        else:
            print(f" {dir_path}/ NOT found")
            all_ok = False
    
    return all_ok

def main():
    print("="*50)
    print("VERIFYING PROJECT SETUP")
    print("="*50)
    
    results = []
    
    print("\n1. Checking Python version...")
    results.append(check_python_version())
    
    print("\n2. Checking packages...")
    results.append(check_packages())
    
    print("\n3. Checking GPU availability...")
    check_gpu()  # Not critical
    
    print("\n4. Checking directory structure...")
    results.append(check_directory_structure())
    
    print("\n" + "="*50)
    if all(results):
        print(" ALL CHECKS PASSED! Ready to start.")
    else:
        print(" SOME CHECKS FAILED. Please fix before continuing.")
    print("="*50)

if __name__ == '__main__':
    main()