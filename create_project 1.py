#!/usr/bin/env python
# coding=utf-8
import os
import argparse

# 创建解析器
parser = argparse.ArgumentParser(description='Create a C project directory structure with Makefile or CMakeLists.txt.')
# 添加项目名称参数
parser.add_argument('project_name', type=str, help='The name of the project')
# 添加构建系统选择参数
parser.add_argument('--build', type=str, choices=['make', 'cmake'], default='make', help='The build system to use (default: make)')

# 解析命令行参数
args = parser.parse_args()

# 设置项目名称和构建系统
project_name = args.project_name
build_system = args.build

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
for dir in dirs:
    os.makedirs(dir, exist_ok=True)

# 创建示例源文件和头文件
with open(f"{project_name}/src/main.c", "w") as f:
    f.write("""#include "module.h"
int main() {
    return 0;
}
""")

with open(f"{project_name}/src/module.c", "w") as f:
    f.write("""#include "module.h"
// Module functions
""")

with open(f"{project_name}/include/module.h", "w") as f:
    f.write("""#ifndef MODULE_H
#define MODULE_H
// Module declarations
#endif
""")

# 根据选择创建构建系统文件
if build_system == 'make':
    # 创建Makefile
    makefile_content = f"""CC=gcc
CFLAGS=-g -Wall -Iinclude
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

elif build_system == 'cmake':
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
