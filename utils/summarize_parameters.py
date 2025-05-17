#!/usr/bin/env python3
import csv
import json
import re
import sys
import argparse
from collections import defaultdict

def parse_xml_to_dict(xml_string, parent_path=""):
    """将XML字符串解析为字典，处理多层嵌套，并记录参数路径"""
    # 去除前后空白
    xml_string = xml_string.strip()
    
    # 如果字符串不包含XML标签，则直接返回
    if not re.search(r'<[^/][^>]*>.*?</[^>]*>', xml_string, re.DOTALL):
        return {}
    
    result = {}
    
    # 提取所有顶级标签
    tag_pattern = re.compile(r'<(\w+)>(.*?)</\1>', re.DOTALL)
    matches = tag_pattern.findall(xml_string)
    
    for tag, content in matches:
        tag = tag.strip()
        content = content.strip()
        
        # 构建当前参数的路径
        current_path = f"{parent_path}.{tag}" if parent_path else tag
        
        # 检查内容是否包含嵌套标签
        if re.search(r'<[^/][^>]*>.*?</[^>]*>', content, re.DOTALL):
            # 递归解析嵌套内容
            nested_result = parse_xml_to_dict(content, current_path)
            result.update(nested_result)
        else:
            # 添加参数和值
            if current_path not in result:
                result[current_path] = set()
            result[current_path].add(content)
    
    return result

def summarize_parameters(input_file, output_file):
    """汇总CSV文件中所有参数和值，仅处理<format>中<o>值为advanced_hls的配置文件"""
    # 用于存储所有参数和值的字典
    params_dict = defaultdict(set)
    
    # 计数器
    total_files = 0
    advanced_hls_files = 0
    
    # 增加CSV字段大小限制
    csv.field_size_limit(sys.maxsize)
    
    # 读取CSV文件
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 跳过表头
        
        for i, row in enumerate(reader):
            if len(row) < 2:
                continue
            
            total_files += 1
            profile_id = row[0]
            xml_body = row[1]
            
            try:
                # 提取<format>标签内的内容
                format_match = re.search(r'<format>(.*?)</format>', xml_body, re.DOTALL)
                if not format_match:
                    continue
                
                format_content = format_match.group(1)
                
                # 检查<output>值是否为advanced_hls
                output_match = re.search(r'<output>(.*?)</output>', format_content, re.DOTALL)
                if not output_match or output_match.group(1).strip().lower() != 'advanced_hls':
                    continue
                
                # 只处理<o>为advanced_hls的配置文件
                advanced_hls_files += 1
                
                # 解析XML并提取参数和值
                params = parse_xml_to_dict(format_content)
                
                # 收集参数和值
                for param, values in params.items():
                    params_dict[param].update(values)
                
                # 每处理1000个配置文件打印一次进度
                if (i + 1) % 1000 == 0:
                    print(f"已处理 {i + 1} 个配置文件，其中 {advanced_hls_files} 个为Advanced HLS输出格式...")
            
            except Exception as e:
                print(f"处理配置文件 {profile_id} 时出错: {e}")
    
    # 将结果写入CSV文件
    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["编号", "参数名", "出现过的值"])
        
        # 按参数名排序
        sorted_params = sorted(params_dict.keys())
        
        for i, param in enumerate(sorted_params, 1):
            values = sorted(list(params_dict[param]))
            values_str = json.dumps(values, ensure_ascii=False)
            writer.writerow([i, param, values_str])
    
    print(f"汇总完成。共处理 {total_files} 个配置文件，其中 {advanced_hls_files} 个为Advanced HLS输出格式")
    print(f"共找到 {len(params_dict)} 个参数")
    print(f"结果已写入 {output_file}")

def main():
    parser = argparse.ArgumentParser(description='汇总Encoding.com配置文件中的所有参数和值')
    parser.add_argument('-i', '--input', default='/home/ec2-user/encoding2mc/filtered_encoding_profiles_final.csv',
                        help='输入CSV文件路径 (默认: /home/ec2-user/encoding2mc/filtered_encoding_profiles_final.csv)')
    parser.add_argument('-o', '--output', default='/home/ec2-user/encoding2mc/advanced_hls_parameters_summary.csv',
                        help='输出CSV文件路径 (默认: /home/ec2-user/encoding2mc/advanced_hls_parameters_summary.csv)')
    
    args = parser.parse_args()
    
    summarize_parameters(args.input, args.output)

if __name__ == "__main__":
    main()
