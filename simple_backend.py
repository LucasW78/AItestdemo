#!/usr/bin/env python3
"""
简化的 FastAPI 后端服务
支持基本的文件上传和API响应，用于演示部署
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# 初始化 FastAPI 应用
app = FastAPI(
    title="AI测试用例生成平台 - 简化版",
    description="基于 FastAPI 的简化版后端服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保数据目录存在
DATA_DIR = Path("./data")
UPLOAD_DIR = DATA_DIR / "documents"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 数据模型
class DocumentInfo(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    upload_time: str
    status: str = "已上传"

class TestCaseRequest(BaseModel):
    content: str
    test_type: str = "functional"

class TestCaseResponse(BaseModel):
    id: str
    content: str
    test_type: str
    generated_cases: List[dict]
    created_at: str

class MindMapRequest(BaseModel):
    content: str
    style: str = "mindmap"

class MindMapResponse(BaseModel):
    id: str
    content: str
    style: str
    nodes: List[dict]
    created_at: str

# 模拟数据存储
documents_db = []
testcases_db = []
mindmaps_db = []

# API 路由
@app.get("/")
async def root():
    return {
        "message": "AI测试用例生成平台 API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ai-test-platform-backend"
    }

@app.get("/api/v1/documents", response_model=List[DocumentInfo])
async def get_documents():
    """获取文档列表"""
    return documents_db

@app.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传文档"""
    try:
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        safe_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / safe_filename

        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 创建文档记录
        doc_info = DocumentInfo(
            id=file_id,
            filename=file.filename,
            file_type=file_extension[1:] if file_extension else "unknown",
            file_size=len(content),
            upload_time=datetime.now().isoformat(),
            status="已上传"
        )
        documents_db.append(doc_info)

        return {
            "message": "文件上传成功",
            "document_id": file_id,
            "filename": file.filename,
            "size": len(content)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@app.post("/api/v1/testcases/generate", response_model=TestCaseResponse)
async def generate_test_cases(request: TestCaseRequest):
    """生成测试用例"""
    try:
        # 增强的AI测试用例生成逻辑
        test_cases = []
        content = request.content.strip()

        if not content:
            raise HTTPException(status_code=400, detail="输入内容不能为空")

        # 根据内容类型智能生成测试用例
        if "登录" in content or "login" in content.lower():
            test_cases.extend(generate_login_test_cases(request.test_type))
        elif "注册" in content or "register" in content.lower():
            test_cases.extend(generate_register_test_cases(request.test_type))
        elif "搜索" in content or "search" in content.lower():
            test_cases.extend(generate_search_test_cases(request.test_type))
        elif "购买" in content or "buy" in content.lower() or "支付" in content:
            test_cases.extend(generate_purchase_test_cases(request.test_type))
        else:
            test_cases.extend(generate_general_test_cases(content, request.test_type))

        # 确保至少有3个测试用例
        while len(test_cases) < 3:
            test_cases.append(create_generic_test_case(len(test_cases) + 1, request.test_type))

        response = TestCaseResponse(
            id=str(uuid.uuid4()),
            content=request.content,
            test_type=request.test_type,
            generated_cases=test_cases,
            created_at=datetime.now().isoformat()
        )

        testcases_db.append(response)
        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成测试用例失败: {str(e)}")

@app.post("/api/v1/testcases/generate-from-text", response_model=TestCaseResponse)
async def generate_test_cases_from_text(
    content: str = Form(..., description="要生成测试用例的文本内容"),
    test_type: str = Form(default="functional", description="测试类型"),
    scenario: str = Form(default="", description="测试场景描述")
):
    """从文本内容生成测试用例（专门用于在线文本输入）"""
    try:
        if not content.strip():
            raise HTTPException(status_code=400, detail="输入内容不能为空")

        # 增强的文本分析
        content = content.strip()
        test_cases = []

        # 根据场景智能生成测试用例
        if scenario:
            # 根据用户提供的场景生成
            test_cases.extend(generate_scenario_based_test_cases(content, scenario, test_type))
        else:
            # 根据内容智能识别场景
            test_cases.extend(generate_context_aware_test_cases(content, test_type))

        # 确保至少有5个测试用例（文本输入通常需要更全面的测试）
        while len(test_cases) < 5:
            test_cases.append(create_enhanced_test_case(len(test_cases) + 1, content, test_type))

        response = TestCaseResponse(
            id=str(uuid.uuid4()),
            content=content,
            test_type=test_type,
            generated_cases=test_cases,
            created_at=datetime.now().isoformat()
        )

        testcases_db.append(response)
        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成测试用例失败: {str(e)}")

def generate_scenario_based_test_cases(content, scenario, test_type):
    """基于场景生成测试用例"""
    test_cases = []

    # 基础功能测试
    test_cases.append({
        "id": str(uuid.uuid4()),
        "title": "测试用例 1: 基础功能验证",
        "description": f"验证'{scenario}'的基础功能是否正常工作",
        "steps": [
            f"1. 准备{scenario}的测试环境",
            "2. 输入测试数据: {content[:50]}...",
            "3. 执行主要功能操作",
            "4. 验证功能响应和结果",
            "5. 检查系统状态和数据完整性"
        ],
        "expected_result": f"{scenario}功能正常运行，结果符合预期",
        "priority": "高",
        "test_type": test_type,
        "category": "功能测试",
        "scenario": scenario
    })

    # 正向流程测试
    test_cases.append({
        "id": str(uuid.uuid4()),
        "title": "测试用例 2: 正向流程测试",
        "description": f"验证{scenario}的正常业务流程",
        "steps": [
            f"1. 按照标准流程执行{scenario}",
            "2. 在每个关键步骤验证状态",
            "3. 确认数据流转正确",
            "4. 验证最终结果",
            "5. 检查日志记录"
        ],
        "expected_result": "整个流程执行顺畅，各步骤结果正确",
        "priority": "高",
        "test_type": test_type,
        "category": "流程测试",
        "scenario": scenario
    })

    # 异常处理测试
    test_cases.append({
        "id": str(uuid.uuid4()),
        "title": "测试用例 3: 异常处理验证",
        "description": f"验证{scenario}在异常情况下的处理能力",
        "steps": [
            "1. 模拟各种异常输入情况",
            "2. 测试网络中断等环境异常",
            "3. 验证错误处理机制",
            "4. 检查异常恢复能力",
            "5. 确认用户体验友好"
        ],
        "expected_result": "异常处理正确，系统能够优雅降级或恢复",
        "priority": "中",
        "test_type": test_type,
        "category": "异常测试",
        "scenario": scenario
    })

    # 性能测试（如果是性能类型）
    if test_type == "performance":
        test_cases.append({
            "id": str(uuid.uuid4()),
            "title": "测试用例 4: 性能基准测试",
            "description": f"验证{scenario}的性能表现",
            "steps": [
                "1. 设置性能测试基准",
                "2. 执行并发测试",
                "3. 测量响应时间",
                "4. 监控资源使用",
                "5. 对比性能指标"
            ],
            "expected_result": "性能指标符合预期，系统稳定运行",
            "priority": "中",
            "test_type": test_type,
            "category": "性能测试",
            "scenario": scenario
        })

    return test_cases

def generate_context_aware_test_cases(content, test_type):
    """基于内容智能生成测试用例"""
    test_cases = []

    # 分析内容特征
    content_lower = content.lower()

    if any(keyword in content_lower for keyword in ["登录", "login", "账号", "密码"]):
        test_cases.extend(generate_login_test_cases(test_type))
    elif any(keyword in content_lower for keyword in ["注册", "register", "注册", "账号"]):
        test_cases.extend(generate_register_test_cases(test_type))
    elif any(keyword in content_lower for keyword in ["搜索", "search", "查询", "检索"]):
        test_cases.extend(generate_search_test_cases(test_type))
    elif any(keyword in content_lower for keyword in ["购买", "buy", "支付", "付款", "订单"]):
        test_cases.extend(generate_purchase_test_cases(test_type))
    else:
        # 通用测试用例
        test_cases.extend(generate_general_test_cases(content, test_type))

    return test_cases

def create_enhanced_test_case(number, content, test_type):
    """创建增强的测试用例"""
    return {
        "id": str(uuid.uuid4()),
        "title": f"测试用例 {number}: 补充验证测试",
        "description": f"基于内容'{content[:30]}...'的补充测试用例",
        "steps": [
            "1. 分析测试需求",
            "2. 设计测试场景",
            "3. 执行测试操作",
            "4. 记录测试结果",
            "5. 验证系统响应"
        ],
        "expected_result": "测试通过，系统功能正常",
        "priority": "低",
        "test_type": test_type,
        "category": "补充测试"
    }

def generate_login_test_cases(test_type):
    """生成登录相关的测试用例"""
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 1: 正常登录功能",
            "description": "验证用户使用正确的用户名和密码能够成功登录系统",
            "steps": [
                "1. 打开登录页面",
                "2. 输入有效的用户名",
                "3. 输入正确的密码",
                "4. 点击登录按钮",
                "5. 验证是否跳转到主页"
            ],
            "expected_result": "用户成功登录，跳转到系统主页",
            "priority": "高",
            "test_type": test_type,
            "category": "功能测试"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 2: 错误密码登录",
            "description": "验证用户使用错误的密码无法登录系统",
            "steps": [
                "1. 打开登录页面",
                "2. 输入有效的用户名",
                "3. 输入错误的密码",
                "4. 点击登录按钮",
                "5. 验证是否显示错误提示"
            ],
            "expected_result": "登录失败，显示'用户名或密码错误'提示",
            "priority": "高",
            "test_type": test_type,
            "category": "异常测试"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 3: 空用户名登录",
            "description": "验证用户不输入用户名时的系统反应",
            "steps": [
                "1. 打开登录页面",
                "2. 用户名输入框留空",
                "3. 输入任意密码",
                "4. 点击登录按钮",
                "5. 验证验证提示信息"
            ],
            "expected_result": "登录失败，显示'请输入用户名'提示",
            "priority": "中",
            "test_type": test_type,
            "category": "边界测试"
        }
    ]

def generate_register_test_cases(test_type):
    """生成注册相关的测试用例"""
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 1: 正常注册流程",
            "description": "验证新用户能够成功注册账户",
            "steps": [
                "1. 打开注册页面",
                "2. 输入有效的用户名",
                "3. 输入有效的邮箱",
                "4. 输入密码和确认密码",
                "5. 点击注册按钮",
                "6. 验证注册成功提示"
            ],
            "expected_result": "注册成功，跳转到登录页面或主页",
            "priority": "高",
            "test_type": test_type,
            "category": "功能测试"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 2: 重复用户名注册",
            "description": "验证使用已存在的用户名注册时的系统处理",
            "steps": [
                "1. 打开注册页面",
                "2. 输入已存在的用户名",
                "3. 输入有效的邮箱",
                "4. 输入密码和确认密码",
                "5. 点击注册按钮",
                "6. 验证错误提示信息"
            ],
            "expected_result": "注册失败，显示'用户名已存在'提示",
            "priority": "高",
            "test_type": test_type,
            "category": "异常测试"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 3: 密码确认不匹配",
            "description": "验证密码和确认密码不一致时的处理",
            "steps": [
                "1. 打开注册页面",
                "2. 输入新的用户名",
                "3. 输入有效的邮箱",
                "4. 输入密码",
                "5. 输入不同的确认密码",
                "6. 点击注册按钮"
            ],
            "expected_result": "注册失败，显示'两次密码输入不一致'提示",
            "priority": "中",
            "test_type": test_type,
            "category": "数据验证测试"
        }
    ]

def generate_search_test_cases(test_type):
    """生成搜索相关的测试用例"""
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 1: 关键词搜索",
            "description": "验证用户能够通过关键词搜索到相关内容",
            "steps": [
                "1. 打开搜索页面",
                "2. 在搜索框中输入关键词",
                "3. 点击搜索按钮",
                "4. 验证搜索结果列表",
                "5. 检查结果相关性"
            ],
            "expected_result": "显示相关的搜索结果列表",
            "priority": "高",
            "test_type": test_type,
            "category": "功能测试"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 2: 空搜索条件",
            "description": "验证不输入搜索条件时的系统处理",
            "steps": [
                "1. 打开搜索页面",
                "2. 搜索框留空",
                "3. 点击搜索按钮",
                "4. 验证系统响应"
            ],
            "expected_result": "显示提示信息或显示所有内容",
            "priority": "中",
            "test_type": test_type,
            "category": "边界测试"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 3: 无结果搜索",
            "description": "验证搜索无结果时的用户体验",
            "steps": [
                "1. 打开搜索页面",
                "2. 输入不存在的关键词",
                "3. 点击搜索按钮",
                "4. 验证无结果提示"
            ],
            "expected_result": "显示'未找到相关结果'的友好提示",
            "priority": "低",
            "test_type": test_type,
            "category": "用户体验测试"
        }
    ]

def generate_purchase_test_cases(test_type):
    """生成购买相关的测试用例"""
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 1: 正常购买流程",
            "description": "验证用户能够完成完整的购买流程",
            "steps": [
                "1. 浏览商品列表",
                "2. 选择商品加入购物车",
                "3. 进入购物车页面",
                "4. 点击结算按钮",
                "5. 选择支付方式",
                "6. 完成支付",
                "7. 验证订单状态"
            ],
            "expected_result": "购买成功，生成订单号，显示支付成功页面",
            "priority": "高",
            "test_type": test_type,
            "category": "业务流程测试"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 2: 支付失败处理",
            "description": "验证支付失败时的系统处理",
            "steps": [
                "1. 完成商品选择",
                "2. 进入支付页面",
                "3. 选择支付方式",
                "4. 模拟支付失败",
                "5. 验证错误处理"
            ],
            "expected_result": "显示支付失败提示，提供重新支付选项",
            "priority": "高",
            "test_type": test_type,
            "category": "异常处理测试"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 3: 库存不足处理",
            "description": "验证商品库存不足时的购买限制",
            "steps": [
                "1. 选择库存不足的商品",
                "2. 尝试加入购物车",
                "3. 验证库存提示",
                "4. 尝试结算"
            ],
            "expected_result": "显示库存不足提示，禁止购买",
            "priority": "中",
            "test_type": test_type,
            "category": "业务规则测试"
        }
    ]

def generate_general_test_cases(content, test_type):
    """生成通用测试用例"""
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 1: 基本功能验证",
            "description": f"基于'{content[:30]}...'内容的基本功能测试",
            "steps": [
                "1. 准备测试环境",
                "2. 执行主要功能操作",
                "3. 验证功能响应",
                "4. 检查结果正确性"
            ],
            "expected_result": "功能正常运行，结果符合预期",
            "priority": "高",
            "test_type": test_type,
            "category": "功能测试"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "测试用例 2: 边界条件测试",
            "description": f"验证'{content[:30]}...'在边界条件下的表现",
            "steps": [
                "1. 测试最小输入条件",
                "2. 测试最大输入条件",
                "3. 测试特殊字符输入",
                "4. 验证系统响应"
            ],
            "expected_result": "系统在各种边界条件下都能正常处理",
            "priority": "中",
            "test_type": test_type,
            "category": "边界测试"
        }
    ]

def create_generic_test_case(number, test_type):
    """创建通用测试用例"""
    return {
        "id": str(uuid.uuid4()),
        "title": f"测试用例 {number}: 附加测试",
        "description": "补充测试用例，确保测试覆盖率",
        "steps": [
            "1. 设置测试条件",
            "2. 执行测试操作",
            "3. 记录测试结果",
            "4. 验证系统状态"
        ],
        "expected_result": "测试通过，系统状态正常",
        "priority": "低",
        "test_type": test_type,
        "category": "补充测试"
    }

@app.post("/api/v1/mindmaps/generate", response_model=MindMapResponse)
async def generate_mind_map(request: MindMapRequest):
    """生成思维导图"""
    try:
        # 模拟AI生成思维导图
        nodes = [
            {
                "id": "root",
                "label": request.content[:50] + "..." if len(request.content) > 50 else request.content,
                "level": 0,
                "x": 400,
                "y": 300
            },
            {
                "id": "node1",
                "label": "功能模块1",
                "level": 1,
                "x": 300,
                "y": 200,
                "parent": "root"
            },
            {
                "id": "node2",
                "label": "功能模块2",
                "level": 1,
                "x": 500,
                "y": 200,
                "parent": "root"
            },
            {
                "id": "node3",
                "label": "子功能1",
                "level": 2,
                "x": 200,
                "y": 100,
                "parent": "node1"
            }
        ]

        response = MindMapResponse(
            id=str(uuid.uuid4()),
            content=request.content,
            style=request.style,
            nodes=nodes,
            created_at=datetime.now().isoformat()
        )

        mindmaps_db.append(response)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成思维导图失败: {str(e)}")

@app.get("/api/v1/testcases", response_model=List[TestCaseResponse])
async def get_test_cases():
    """获取测试用例列表"""
    return testcases_db

@app.get("/api/v1/mindmaps", response_model=List[MindMapResponse])
async def get_mind_maps():
    """获取思维导图列表"""
    return mindmaps_db

@app.get("/api/v1/stats")
async def get_stats():
    """获取统计信息"""
    return {
        "documents_count": len(documents_db),
        "testcases_count": len(testcases_db),
        "mindmaps_count": len(mindmaps_db),
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn

    print("🚀 启动AI测试用例生成平台后端服务...")
    print("📍 服务地址: http://localhost:8080")
    print("📖 API文档: http://localhost:8080/docs")
    print("❤️ 健康检查: http://localhost:8080/health")

    uvicorn.run(
        "simple_backend:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )