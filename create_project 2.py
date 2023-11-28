#!/usr/bin/env python
# coding=utf-8
import os
import argparse
import datetime
# 创建解析器
parser = argparse.ArgumentParser(description='Create a C project directory structure with Makefile or CMakeLists.txt.')
# 添加项目名称参数
parser.add_argument('project_name', type=str, help='The name of the project')
# 添加构建系统选择参数
parser.add_argument('-b','--build', type=str, choices=['make', 'cmake'], default='make', help='The build system to use (default: make)')
# 添加模块名称列表参数
parser.add_argument('-m','--modules', type=str, help='Comma-separated list of module names to create .c and .h files for')

# 解析命令行参数
args = parser.parse_args()

# 设置项目名称和构建系统
project_name = args.project_name
build_system = args.build
modules = args.modules.split(',') if args.modules else []

def get_prefix(file):
    # 获取当前日期  
    now = datetime.datetime.now()  
    # date = now.strftime("%Y-%m-%d")
    
    # 定义元数据  
    metadata = {  
        'Author': 'Wen Quanshan',  
        'License': 'MIT',  
        'Description': 'xxx',  
        'File': os.path.basename(file),  
        'Date': now.strftime("%Y-%m-%d"), 
        'Time': now.strftime("%H:%M:%S"), 
    }

    # 构造新的文件内容  
    # prefix = f"/*\n * @file {metadata['File']}\n * @date {metadata['Date']}\n * @author {metadata['Author']}\n * @license {metadata['License']}\n * @description {metadata['Description']}\n */\n"
    prefix=f"""/*
 * @file {file}
 * @date {metadata['Date']}
 * @time {metadata['Time']}
 * @author {metadata['Author']}
 * @license {metadata['License']}
 * @description {metadata['Description']}
 */
"""
    return prefix

# 定义目录结构
dirs = [
    f"{project_name}/src",
    f"{project_name}/include",
    f"{project_name}/lib",
    f"{project_name}/bin",
    f"{project_name}/obj",
    f"{project_name}/test",
    f"{project_name}/docs"
]

# 创建目录
for subdir in dirs:
    if not os.path.exists(subdir):
        os.makedirs(subdir)

# 创建模块源文件和头文件
for module in modules:
    prefix = get_prefix(module)
    # print(prefix)
    source_path = f"{project_name}/src/{module}.c"
    header_path = f"{project_name}/include/{module}.h"
    if not os.path.exists(source_path):
        with open(source_path, "w") as f:
            f.write(f"{prefix}\n")
            f.write(f"""#include "{module}.h"
// {module} functions
""")
    if not os.path.exists(header_path):
        with open(header_path, "w") as f:
            f.write(f"{prefix}\n")
            f.write(f"""#ifndef {module.upper()}_H
#define {module.upper()}_H
// {module} declarations
#endif
""")

# 创建示例源文件和头文件
source_files = {
    f"{project_name}/src/main.c": """#include "module.h"
int main() {
    return 0;
}
"""
}

for file_path, content in source_files.items():
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write(content)

# 根据选择创建构建系统文件
if build_system == 'make' and not os.path.exists(f"{project_name}/Makefile"):
    # 创建Makefile
    makefile_content = f"""CC=gcc
CFLAGS=-g -Wall -Wl,-rpath,. -Iinclude
LDFLAGS=-Llib
SRC_DIR=src
OBJ_DIR=obj
BIN_DIR=bin

SOURCES=$(wildcard $(SRC_DIR)/*.c)
OBJECTS=$(SOURCES:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)
TARGET=$(BIN_DIR)/{project_name}

all: $(TARGET)

$(TARGET): $(OBJECTS)
\t$(CC) $(LDFLAGS) $^ -o $@

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
\t$(CC) $(CFLAGS) -c $< -o $@

clean:
\trm -f $(OBJ_DIR)/*.o $(TARGET)

.PHONY: all clean
"""

    with open(f"{project_name}/Makefile", "w") as f:
        f.write(makefile_content)

elif build_system == 'cmake' and not os.path.exists(f"{project_name}/CMakeLists.txt"):
    # 创建CMakeLists.txt
    cmakelists_content = f"""cmake_minimum_required(VERSION 3.10)

# 设置项目名称和版本
project({project_name} VERSION 1.0)

# 指定 C 标准
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED True)

# 设置默认构建类型为 Debug
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()

# 设置输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/lib)

# 添加可执行文件
add_executable(${{PROJECT_NAME}} src/main.c)

# 设置调试和发布特定的编译器标志
target_compile_options(${{PROJECT_NAME}} PRIVATE
  $<$<CONFIG:Debug>:-g>
  $<$<CONFIG:Release>:-O3>
)

install(TARGETS ${{PROJECT_NAME}} DESTINATION bin)
"""

    with open(f"{project_name}/CMakeLists.txt", "w") as f:
        f.write(cmakelists_content)

print(f"{project_name} directory structure with {build_system} build system created successfully.")
