#!/usr/bin/env python3
import os
import csv
import shutil
import xml.etree.ElementTree as ET
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('FileOrganizer')

def get_output_type(xml_file):
    """从XML文件中提取output类型"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        output_element = root.find('.//format/output')
        if output_element is not None and output_element.text:
            return output_element.text.strip()
        else:
            logger.warning(f"No output type found in {xml_file}")
            return None
    except Exception as e:
        logger.error(f"Error parsing {xml_file}: {str(e)}")
        return None

def main():
    # 读取CSV文件
    csv_file = '/home/ec2-user/e2mc_assistant/pilot_formats_v2.csv'
    source_dir = '/home/ec2-user/e2mc_assistant/encoding_profiles'
    target_dir = '/home/ec2-user/e2mc_assistant/encoding_profiles/pilot1'
    
    # 确保目标目录存在
    os.makedirs(target_dir, exist_ok=True)
    
    # 读取CSV文件中的ID
    pilot_ids = set()
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pilot_ids.add(row['format_id'])
    
    logger.info(f"Found {len(pilot_ids)} IDs in CSV file")
    
    # 处理的文件计数
    processed_count = 0
    
    # 遍历源目录中的XML文件
    for filename in os.listdir(source_dir):
        if not filename.endswith('.xml'):
            continue
            
        # 检查文件名是否匹配CSV中的ID
        file_id = filename.split('.')[0]
        if file_id not in pilot_ids:
            continue
            
        # 获取XML文件的完整路径
        source_file = os.path.join(source_dir, filename)
        
        # 从XML文件中提取output类型
        output_type = get_output_type(source_file)
        if not output_type:
            logger.warning(f"Skipping {filename} due to missing output type")
            continue
            
        # 创建目标目录（如果不存在）
        output_dir = os.path.join(target_dir, output_type)
        os.makedirs(output_dir, exist_ok=True)
        
        # 复制文件到目标目录
        target_file = os.path.join(output_dir, filename)
        shutil.copy2(source_file, target_file)
        
        logger.info(f"Copied {filename} to {output_type}/")
        processed_count += 1
    
    logger.info(f"Processed {processed_count} files")

if __name__ == "__main__":
    main()
