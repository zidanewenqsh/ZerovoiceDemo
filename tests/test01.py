import os  
import datetime  

def add_metadata_to_file(file_path):  
    # 获取当前日期  
    now = datetime.datetime.now()  
    date = now.strftime("%Y-%m-%d")  

    # 定义元数据  
    metadata = {  
        'Author': 'Tom',  
        'License': 'MIT',  
        'Description': 'xxx',  
        'File': os.path.basename(file_path),  
        'Date': date, 
        'Time': now.strftime("%H:%M:%S"), 
    }  

    # 读取文件内容  
    # with open(file_path, 'r') as f:  
    #     content = f.read()  

    # 构造新的文件内容  
    # prefix = f"/*\n * @file {metadata['File']}\n * @date {metadata['Date']}\n * @author {metadata['Author']}\n * @license {metadata['License']}\n * @description {metadata['Description']}\n */\n"
    prefix=f"""/*
 * @file {file_path}
 * @time {metadata['Time']}
 * @author {metadata['Author']}
 * @license {metadata['License']}
 * @description {metadata['Description']}
 */
    """


    print(prefix)

    # # 写入新的文件内容  
    # with open(file_path, 'w') as f:  
    #     f.write(new_content)  

def main():  
    # 指定要处理的目录路径  
    directory = '.'  

    # 遍历目录中的所有文件  
    for root, _, files in os.walk(directory):  
        for file in files:  
            # 如果文件扩展名是 .c 或 .h，则在文件开头添加元数据  
            if file.endswith('.c') or file.endswith('.h'):  
                # file_path = os.path.join(root, file)  
                add_metadata_to_file(file)  
                print(f"Processed {file}")  

if __name__ == "__main__":  
    main()