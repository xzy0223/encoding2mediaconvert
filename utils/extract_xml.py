#!/usr/bin/env python3
"""
提取CSV文件中的XML内容并保存为单独的XML文件

此脚本从source_profile目录中的CSV文件读取数据，
提取xml_body列的内容，并将其保存为单独的XML文件，
文件名前缀为对应行的id值。
所有XML文件将保存到encoding_profiles目录中。
"""

import os
import csv
import glob
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_xml_from_csv(csv_file_path, output_dir):
    """
    从CSV文件中提取XML内容并保存为单独的XML文件
    
    Args:
        csv_file_path: CSV文件的路径
        output_dir: 输出XML文件的目录
    """
    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info(f"开始处理CSV文件: {csv_file_path}")
    
    # 计数器
    processed_count = 0
    error_count = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            # 使用csv模块读取CSV文件
            csv_reader = csv.DictReader(csv_file)
            
            # 检查必要的列是否存在
            if 'id' not in csv_reader.fieldnames:
                logger.error(f"CSV文件缺少必要的列 'id'")
                return
            
            # 检查xml_body列或original_xml_body列是否存在
            xml_column = 'xml_body' if 'xml_body' in csv_reader.fieldnames else 'original_xml_body'
            if xml_column not in csv_reader.fieldnames:
                logger.error(f"CSV文件缺少XML内容列 'xml_body' 或 'original_xml_body'")
                return
            
            logger.info(f"使用列 '{xml_column}' 作为XML内容来源")
            
            # 处理每一行
            for row in csv_reader:
                try:
                    id_value = row['id']
                    xml_content = row[xml_column]
                    
                    if not id_value or not xml_content:
                        logger.warning(f"跳过空ID或空XML内容的行")
                        continue
                    
                    # 创建XML文件路径
                    xml_file_path = os.path.join(output_dir, f"{id_value}.xml")
                    
                    # 写入XML内容到文件
                    with open(xml_file_path, 'w', encoding='utf-8') as xml_file:
                        xml_file.write(xml_content)
                    
                    processed_count += 1
                    if processed_count % 100 == 0:
                        logger.info(f"已处理 {processed_count} 个XML文件")
                        
                except Exception as e:
                    logger.error(f"处理行时出错: {str(e)}")
                    error_count += 1
    
    except Exception as e:
        logger.error(f"读取CSV文件时出错: {str(e)}")
        return
    
    logger.info(f"处理完成! 成功提取 {processed_count} 个XML文件, 错误 {error_count} 个")

def main():
    """主函数"""
    # 定义源目录和目标目录
    source_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'source_profile')
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'encoding_profiles')
    
    # 查找source_profile目录中的所有CSV文件
    csv_files = glob.glob(os.path.join(source_dir, '*.csv'))
    
    if not csv_files:
        logger.error(f"在 {source_dir} 中没有找到CSV文件")
        return
    
    # 处理每个CSV文件
    for csv_file in csv_files:
        extract_xml_from_csv(csv_file, output_dir)

if __name__ == "__main__":
    main()
