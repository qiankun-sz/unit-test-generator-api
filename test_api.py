#!/usr/bin/env python3
"""
Zapier API测试脚本
测试单元测试生成器API端点的功能性和兼容性
"""

import sys
import json
import asyncio
import requests
from typing import Dict, Any, List

def test_python_function():
    """测试Python函数生成单元测试"""
    print("测试1: Python函数（pytest框架）")
    
    payload = {
        "code_snippet": """def calculate_discount(order_total: float, is_premium: bool = False) -> float:
    '''
    计算订单折扣
    
    Args:
        order_total: 订单总额
        is_premium: 是否为高级会员
        
    Returns:
        折扣后的金额
        
    Raises:
        ValueError: 订单总额小于等于0
    '''
    if order_total <= 0:
        raise ValueError("订单总额必须大于0")
    
    base_discount = 0.05  # 基础折扣5%
    if is_premium:
        base_discount += 0.1  # 高级会员额外10%
    
    discount_amount = order_total * base_discount
    return order_total - discount_amount""",
        "language": "python",
        "test_framework": "pytest",
        "test_strategy": "comprehensive",
        "coverage_target": 85
    }
    
    return payload

def test_javascript_function():
    """测试JavaScript函数生成单元测试"""
    print("测试2: JavaScript函数（Jest框架）")
    
    payload = {
        "code_snippet": """/**
 * 计算数组元素的总和
 * @param {number[]} arr - 数值数组
 * @returns {number} 数组元素的总和
 * @throws {Error} 如果输入不是数组或包含非数字
 */
function sumArray(arr) {
    if (!Array.isArray(arr)) {
        throw new Error('Input must be an array');
    }
    
    if (arr.length === 0) {
        return 0;
    }
    
    // 验证所有元素都是数字
    if (!arr.every(item => typeof item === 'number')) {
        throw new Error('Array must contain only numbers');
    }
    
    return arr.reduce((total, current) => total + current, 0);
}""",
        "language": "javascript",
        "test_framework": "jest",
        "test_strategy": "boundary_only",
        "coverage_target": 80
    }
    
    return payload

def test_java_method():
    """测试Java方法生成单元测试"""
    print("测试3: Java方法（JUnit框架）")
    
    payload = {
        "code_snippet": """/**
 * 计算阶乘
 * @param n 非负整数
 * @return n的阶乘
 * @throws IllegalArgumentException 如果n小于0
 */
public static int factorial(int n) {
    if (n < 0) {
        throw new IllegalArgumentException("n must be non-negative");
    }
    
    if (n == 0 || n == 1) {
        return 1;
    }
    
    int result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    
    return result;
}""",
        "language": "java",
        "test_framework": "junit",
        "test_strategy": "comprehensive",
        "coverage_target": 90
    }
    
    return payload

async def test_api_endpoint(base_url: str, test_cases: List[Dict[str, Any]]):
    """测试API端点"""
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n执行测试用例 {i}: {test_case.get('language', 'unknown')}")
        
        try:
            # 发送POST请求
            response = requests.post(
                f"{base_url}/api/v1/generate-tests",
                json=test_case,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            # 检查响应状态
            if response.status_code == 200:
                result = response.json()
                
                if result.get("status") == "success":
                    print(f"  ✓ 成功: 生成 {len(result.get('generated_tests', '').split(chr(10)))} 行测试代码")
                    print(f"  ✓ 预估覆盖率: {result.get('coverage_estimate', 0)}%")
                    
                    token_usage = result.get("token_usage", {})
                    if token_usage:
                        print(f"  ✓ Token消耗: 输入={token_usage.get('input_tokens', 0)}, 输出={token_usage.get('output_tokens', 0)}")
                    
                    # 验证中心计量服务记录
                    print(f"  ✓ 请求ID: {result.get('request_id', 'N/A')}")
                    
                    results.append({
                        "test_case": i,
                        "status": "success",
                        "coverage": result.get("coverage_estimate", 0),
                        "token_usage": token_usage,
                        "request_id": result.get("request_id")
                    })
                    
                else:
                    print(f"  ✗ 失败: {result.get('message', '未知错误')}")
                    results.append({
                        "test_case": i,
                        "status": "error",
                        "error": result.get("message", "未知错误")
                    })
                    
            else:
                print(f"  ✗ HTTP错误: {response.status_code}")
                print(f"    响应内容: {response.text[:200]}")
                results.append({
                    "test_case": i,
                    "status": "http_error",
                    "status_code": response.status_code
                })
                
        except requests.exceptions.Timeout:
            print(f"  ✗ 请求超时")
            results.append({
                "test_case": i,
                "status": "timeout"
            })
            
        except requests.exceptions.ConnectionError:
            print(f"  ✗ 连接错误 - 请检查API服务器是否运行")
            results.append({
                "test_case": i,
                "status": "connection_error"
            })
            
        except Exception as e:
            print(f"  ✗ 异常: {str(e)}")
            results.append({
                "test_case": i,
                "status": "exception",
                "error": str(e)
            })
    
    return results

def generate_test_report(results: List[Dict[str, Any]], base_url: str):
    """生成测试报告"""
    print("\n" + "="*60)
    print("API测试报告")
    print("="*60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r.get("status") == "success")
    failure_tests = total_tests - successful_tests
    
    print(f"测试总数: {total_tests}")
    print(f"成功测试: {successful_tests}")
    print(f"失败测试: {failure_tests}")
    print(f"成功率: {(successful_tests/total_tests*100):.1f}%")
    
    # 详细结果
    print("\n详细结果:")
    for result in results:
        test_num = result.get("test_case")
        status = result.get("status")
        
        if status == "success":
            coverage = result.get("coverage", 0)
            token_usage = result.get("token_usage", {})
            print(f"  测试{test_num}: ✓ 成功 (覆盖率: {coverage}%, Tokens: {token_usage.get('total_tokens', 0)})")
        else:
            error = result.get("error", "未知错误")
            print(f"  测试{test_num}: ✗ 失败 ({error})")
    
    # 建议
    print("\n建议:")
    if successful_tests == total_tests:
        print("  ✓ 所有测试通过，API可以用于Zapier集成")
        print(f"  ✓ API端点: {base_url}/api/v1/generate-tests")
        print("  ✓ 请继续在Zapier开发者平台配置Action")
    else:
        print("  ⚠ 部分测试失败，请检查:")
        print("    1. API服务器是否正常运行")
        print("    2. DEEPSEEK_API_KEY环境变量是否正确设置")
        print("    3. 网络连接是否正常")
        print("    4. 防火墙是否允许API访问")
    
    print("\n下一步:")
    print("  1. 确保API服务器在公网可访问")
    print("  2. 配置HTTPS证书（Zapier要求HTTPS）")
    print("  3. 在Zapier开发者平台创建Action")
    print("  4. 测试Zapier Action调用")
    print("  5. 提交到Zapier App Directory审核")

async def main():
    """主函数"""
    print("Zapier API测试脚本")
    print("="*60)
    
    # 配置API基础URL
    # 默认使用本地测试，实际部署后需要修改为公网URL
    base_url = "http://localhost:8080"
    
    # 允许命令行参数指定URL
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"API基础URL: {base_url}")
    print("测试前请确保API服务器已启动")
    
    # 创建测试用例
    test_cases = [
        test_python_function(),
        test_javascript_function(),
        test_java_method()
    ]
    
    # 测试API端点
    print("\n开始API测试...")
    results = await test_api_endpoint(base_url, test_cases)
    
    # 生成报告
    generate_test_report(results, base_url)
    
    # 返回退出代码
    success_count = sum(1 for r in results if r.get("status") == "success")
    if success_count == len(test_cases):
        print("\n所有测试通过 ✓")
        sys.exit(0)
    else:
        print(f"\n测试失败: {len(test_cases)-success_count}个失败 ✗")
        sys.exit(1)

if __name__ == "__main__":
    # 处理异步主函数
    asyncio.run(main())