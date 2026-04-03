"""
setup_cpp.py - تجميع مكتبة C++
"""

import os
import sys
import subprocess
import platform


def compile_cpp():
    """تجميع ملف C++ إلى مكتبة Python"""
    
    print("🔧 Compiling C++ physics engine...")
    
    cpp_file = "cpp/physics.cpp"
    output_name = "physics_cpp"
    
    if not os.path.exists(cpp_file):
        print(f"❌ Error: {cpp_file} not found!")
        return False
    
    system = platform.system()
    
    if system == "Linux" or system == "Darwin":  # Linux or Mac
        cmd = [
            "g++", "-O3", "-shared", "-std=c++17", "-fPIC",
            cpp_file,
            "-o", f"{output_name}.so"
        ]
    elif system == "Windows":
        cmd = [
            "g++", "-O3", "-shared", "-std=c++17", "-fPIC",
            cpp_file,
            "-o", f"{output_name}.pyd"
        ]
    else:  # Android
        # استخدام المترجم الموجود في Pydroid3
        cmd = [
            "aarch64-linux-android-clang++", "-O3", "-shared", "-std=c++17", "-fPIC",
            "-I", "/data/user/0/ru.iiec.pydroid3/files/aarch64-linux-android/include/python3.13",
            cpp_file,
            "-o", f"{output_name}.so"
        ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ C++ compilation successful!")
            if os.path.exists(f"{output_name}.so"):
                print(f"   Output: {output_name}.so")
            return True
        else:
            print(f"❌ Compilation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = compile_cpp()
    if success:
        print("\n🎉 C++ engine ready! Run main.py to start the game.")
    else:
        print("\n⚠️ Compilation failed. The game will run with Python fallback.")