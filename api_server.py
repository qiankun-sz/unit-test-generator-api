#!/usr/bin/env python3
"""
Zapier集成API服务器
为单元测试生成器提供REST API接口，供Zapier Action调用
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.unit_test_generator.main import UnitTestGeneratorApp
from src.unit_test_generator.config import UnitTestGeneratorConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局应用实例
unit_test_app = None

def initialize_app():
    """初始化单元测试生成器应用"""
    global unit_test_app
    try:
        config = UnitTestGeneratorConfig()
        unit_test_app = UnitTestGeneratorApp(config)
        logger.info("单元测试生成器应用初始化成功")
    except Exception as e:
        logger.error(f"应用初始化失败: {e}")
        raise

# 异步函数包装器
async def async_generate_tests(test_request: Dict[str, Any]) -> Dict[str, Any]:
    """异步生成单元测试"""
    if unit_test_app is None:
        initialize_app()
    return await unit_test_app.generate_unit_tests(test_request)

async def async_analyze_code(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """异步分析代码"""
    if unit_test_app is None:
        initialize_app()
    return await unit_test_app.analyze_code(request_data)

# Flask应用
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)  # 允许跨域请求
    
    # 应用启动时初始化
    @app.before_first_request
    def initialize():
        initialize_app()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查端点"""
        return jsonify({
            "status": "healthy",
            "service": "unit-test-generator-api",
            "version": "1.0.0"
        })
    
    @app.route('/api/v1/generate-tests', methods=['POST'])
    def generate_tests():
        """
        生成单元测试的主端点
        请求格式（Zapier兼容）：
        {
            "code_snippet": "def add(a,b): return a+b",
            "language": "python",
            "test_framework": "pytest",
            "test_strategy": "comprehensive",
            "coverage_target": 80
        }
        """
        try:
            # 获取请求数据
            request_data = request.get_json()
            
            if not request_data:
                return jsonify({
                    "status": "error",
                    "error_code": "INVALID_REQUEST",
                    "message": "请求数据为空",
                    "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
                }), 400
            
            # 验证必填字段
            required_fields = ["code_snippet", "language"]
            for field in required_fields:
                if field not in request_data or not request_data[field]:
                    return jsonify({
                        "status": "error",
                        "error_code": "MISSING_FIELD",
                        "message": f"缺少必填字段: {field}",
                        "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
                }), 400
            
            # 转换为单元测试生成器请求格式
            test_request = {
                "request_type": "test_generation",
                "language": request_data["language"],
                "code": request_data["code_snippet"],
                "test_strategy": request_data.get("test_strategy", "comprehensive"),
                "framework_preference": request_data.get("test_framework", ""),
                "coverage_target": request_data.get("coverage_target", 80)
            }
            
            # 调用单元测试生成器（异步）
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(async_generate_tests(test_request))
            loop.close()
            
            # 确保响应包含Zapier所需字段
            if result.get("status") == "success":
                # 补充Zapier特定字段
                result["generated_tests"] = result.get("test_code", "")
                result["coverage_estimate"] = result.get("generated_tests", {}).get(
                    "coverage_estimate", {}
                ).get("line_coverage", 0)
                result["edge_cases_identified"] = result.get("generated_tests", {}).get(
                    "edge_cases", []
                )
                result["mock_configurations"] = result.get("generated_tests", {}).get(
                    "mock_configurations", []
                )
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"API调用异常: {e}", exc_info=True)
            return jsonify({
                "status": "error",
                "error_code": "INTERNAL_ERROR",
                "message": f"内部服务器错误: {str(e)}",
                "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
            }), 500
    
    @app.route('/api/v1/analyze-code', methods=['POST'])
    def analyze_code():
        """代码分析端点"""
        try:
            request_data = request.get_json()
            
            # 验证请求
            if not request_data or "code" not in request_data:
                return jsonify({
                    "status": "error",
                    "message": "缺少代码内容"
                }), 400
            
            # 调用分析功能（异步）
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(async_analyze_code(request_data))
            loop.close()
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"代码分析异常: {e}")
            return jsonify({
                "status": "error",
                "message": f"分析失败: {str(e)}"
            }), 500
    
    if __name__ == '__main__':
        # 获取端口（环境变量或默认）
        port = int(os.getenv('PORT', 8080))
        app.run(host='0.0.0.0', port=port, debug=False)

except ImportError as e:
    logger.error(f"缺少必要的依赖: {e}")
    logger.info("请安装Flask和Flask-CORS: pip install flask flask-cors")
    sys.exit(1)