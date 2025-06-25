# None- Live AST Function Calling

## 项目意义

这个项目是一个专门用于评估大语言模型函数调用能力的测试框架。函数调用（Function Calling）是AI模型理解用户需求并调用相应工具或API的核心能力，对于构建实用的AI应用至关重要。

### 主要功能
- **多场景测试**：支持简单函数调用、并行函数调用和多重函数调用三种测试场景
- **自动化评估**：自动执行测试用例并计算准确率、token使用量等指标
- **标准化格式**：格式进行函数调用
- **详细统计**：提供token使用统计、错误分析等详细报告

### 应用场景
- 评估不同AI模型的函数调用准确性
- 比较不同模型在复杂函数调用场景下的表现
- 为模型选择和优化提供数据支持
- 开发和测试函数调用相关功能

## 项目结构

```
evaluation/
├── function_calling/          # 核心评估逻辑
│   ├── run_eval.py           # 主评估运行器
│   ├── fc_utils.py           # 工具函数
│   ├── fc_score.py           # 评分计算
│   └── FCsimple.py           # 简单测试
├── FC-samples/               # 测试样本
│   ├── simple_FC.json        # 简单函数调用测试
│   ├── multiple_FC.json      # 多重函数调用测试
│   └── parallel_FC.json      # 并行函数调用测试
├── FC-answers/               # 标准答案
│   ├── simple_FC_answers.json
│   ├── multiple_FC_answers.json
│   └── parallel_FC_answers.json
├── json_processing/          # JSON处理工具
│   ├── ast_checker.py        # AST语法检查
│   ├── parse_output.py       # 输出解析
│   └── json_translator.py    # JSON转换
├── config.py                 # 配置文件
└── requirements.txt          # Python依赖
```

## 安装和运行

### 1. 环境要求
- Python 3.8+
- Node.js (用于OpenAI SDK)

### 2. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Node.js依赖
npm install
```

### 3. 配置API密钥

编辑 `config.py` 文件，设置你的API密钥：

```python
MODEL_NAME = "your-siliconflow-model-name"  # 使用的模型名称
SILICONFLOW_API_KEY = "your-api-key-here"  # 你的API密钥
```

### 4. 运行评估

```bash
# 运行完整评估（包括所有三种测试类型）
cd function_calling
python run_eval.py
```

### 5. 查看结果

评估完成后，系统会输出：
- 准确率统计
- Token使用量统计
- 错误分析
- 性能指标

## 测试类型说明

### 1. 简单函数调用 (Simple Function Calling)
- 单个函数调用场景
- 测试模型对基本函数调用的理解能力

### 2. 多重函数调用 (Multiple Function Calling)
- 连续调用多个不同的函数
- 测试模型的逻辑推理和函数组合能力

### 3. 并行函数调用 (Parallel Function Calling)
- 多次调用同一个函数
- 测试模型处理并发任务的能力

## 输出格式

对于每一种测试类别`(simple, parallel, multiple)`会有一下输出：
```json
{
  "accuracy": 0.85,
  "total_count": 100,
  "error_count": 15,
  "token_usage": {
    "total_input_tokens": 5000,
    "total_output_tokens": 2000,
    "total_tokens": 7000,
    "average_tokens_per_call": 70,
    "std_token_usage": 15.5,
    "mean_token_usage": 70.0,
    "percentile_95_token_usage": 95.0
  }
}
```

最后会输出综合分数，综合分数为三种类别测试准确率的均值给出:

`Average score: 0.xxxx`

## 注意事项

1. **API限制**：确保你的API密钥有足够的配额
2. **网络连接**：需要稳定的网络连接访问SiliconFlow API
3. **模型兼容性**：确保使用的模型支持函数调用功能
4. **测试数据**：可以根据需要修改测试样本和答案文件

## 故障排除

### 常见问题
1. **API密钥错误**：检查 `config.py` 中的API密钥是否正确
2. **网络连接问题**：确保能够访问 `https://api.siliconflow.cn`
3. **依赖缺失**：运行 `pip install -r requirements.txt` 安装所有依赖
4. **权限问题**：确保对项目目录有读写权限

### 调试模式
在 `fc_utils.py` 中可以启用调试输出：
```python
# 在make_function_call函数中添加调试信息
print(f"Making function call with prompt: {prompt}")
```

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。在提交代码前，请确保：
1. 代码符合PEP 8规范
2. 添加适当的注释和文档
3. 测试新功能不会破坏现有功能

