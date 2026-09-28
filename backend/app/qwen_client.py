import dashscope
from dashscope import Generation
from app.config import settings

SYSTEM_PROMPT = (
    "你是一个专业的AI文本检测分析器，擅长识别AI生成文本和人类写作的细微差异。"
    "你需要从多个维度综合分析文本特征，包括语言模式、内容结构、写作风格、统计特征等。"
    "重要：现代AI模型生成的文本越来越像人类，你需要更加谨慎和严格地分析。"
    "当文本表现出任何AI特征时，应该倾向于判断为AI生成，而不是过于宽松地判断为人类写作。"
    "只能输出JSON格式的结果，严格按照指定格式返回，不要添加任何其他内容。"
)

# 文档级检测 Prompt（用于整体分析）
DOCUMENT_PROMPT_TMPL = """请仔细分析以下文本是否由AI生成。你需要从多个维度进行综合判断：

【分析维度】
1. 语言模式：检查是否存在过于正式、完美、缺乏变化的表达；注意AI模型常使用流畅但缺乏个性的语言
2. 内容结构：分析段落组织、逻辑连贯性、信息密度；AI文本往往结构过于规整，缺乏自然的跳跃
3. 写作风格：评估用词习惯、句式复杂度、个性化特征；注意是否存在模式化的表达方式
4. 统计特征：观察重复模式、长度分布、标点使用等；AI文本可能在统计特征上过于均匀
5. 细节真实性：检查是否存在过于完美的细节描述，缺乏人类写作中的不完美和随机性
6. 情感表达：评估情感是否真实自然，还是显得过于理性或格式化

【检测原则】
- 现代AI模型生成的文本越来越像人类，需要更加严格和谨慎
- 当文本表现出任何AI特征时，应该倾向于判断为AI生成
- 不要因为文本看起来'有文学性'就轻易判断为人类写作
- 注意AI模型可能生成具有文学性的文本，但这不代表是人类写作
- 如果存在任何疑问，应该倾向于判断为'uncertain'或'ai'，而不是'human'

【待检测文本】
{text}

【输出要求】
请返回JSON格式，包含以下字段：
{{
  "label": "ai"（AI生成）或 "human"（人类写作）或 "uncertain"（不确定）,
  "score": 0到1之间的数字（0表示确定是人类，1表示确定是AI，0.5表示不确定）,
  "confidence": "high"（高置信度）或 "medium"（中等）或 "low"（低置信度）,
  "rationale": "简短的判断理由（1-2句话）",
  "detailed_analysis": "详细的多维度分析（至少200字，涵盖语言模式、内容结构、写作风格、统计特征等方面）",
  "key_indicators": ["最重要的判断依据1", "判断依据2", "判断依据3"],
  "methodology": "使用的检测方法和分析流程说明"
}}

【重要提示】
- 只返回JSON，不要添加任何其他文字、解释或markdown标记
- 确保JSON格式完全正确，可以直接被解析
- detailed_analysis 要详细具体，不要泛泛而谈
- key_indicators 要列出最关键的3-5个判断依据
- 如果文本可能是AI生成但不确定，label应该设为"uncertain"或"ai"，score应该偏向0.5以上"""

# 句子级检测 Prompt（用于精细分析）
SENTENCE_PROMPT_TMPL = (
    "请分析以下句子是否表现出AI生成的特征：\n\n"
    "【待分析句子】\n{sentence}\n\n"
    "【上下文】\n{context}\n\n"
    "【分析重点】\n"
    "1. 句式是否过于完美或正式\n"
    "2. 用词是否缺乏变化或过于重复\n"
    "3. 表达是否缺乏个性化特征\n"
    "4. 与上下文是否自然衔接\n\n"
    "【输出要求】\n"
    "返回JSON格式：\n"
    '{{\n'
    '  "is_ai_likely": true 或 false,\n'
    '  "confidence": "high" 或 "medium" 或 "low",\n'
    '  "reason": "判断理由",\n'
    '  "indicators": ["特征1", "特征2"]\n'
    '}}\n\n'
    "只返回JSON，不要添加其他内容！"
)


def detect_with_qwen(text: str, granularity: str = "document"):
    """
    调用 Qwen 模型进行文本检测
    
    Args:
        text: 待检测文本
        granularity: 检测粒度，"document"（文档级）或 "sentence"（句子级）
    
    Returns:
        模型返回的原始文本
    """
    if not settings.qwen_api_key:
        raise RuntimeError("DASHSCOPE_API_KEY 未配置")
    
    dashscope.api_key = settings.qwen_api_key
    
    # 根据粒度选择不同的 Prompt
    if granularity == "sentence":
        # 句子级检测需要上下文，这里简化处理
        prompt = SENTENCE_PROMPT_TMPL.format(
            sentence=text.strip(),
            context="（上下文信息）"
        )
    else:
        # 文档级检测
        prompt = DOCUMENT_PROMPT_TMPL.format(text=text.strip())
    
    resp = Generation.call(
        model=settings.qwen_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=settings.detect_temperature,
        result_format="message",
        timeout=settings.qwen_timeout,
    )
    content = resp.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
    return content


def detect_sentence_with_context(sentence: str, context: str = ""):
    """
    对单个句子进行检测，提供上下文信息
    
    Args:
        sentence: 待检测的句子
        context: 上下文文本
    
    Returns:
        模型返回的原始文本
    """
    if not settings.qwen_api_key:
        raise RuntimeError("DASHSCOPE_API_KEY 未配置")
    
    dashscope.api_key = settings.qwen_api_key
    prompt = SENTENCE_PROMPT_TMPL.format(
        sentence=sentence.strip(),
        context=context.strip() if context else "（无上下文）"
    )
    
    resp = Generation.call(
        model=settings.qwen_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=settings.detect_temperature,
        result_format="message",
        timeout=settings.qwen_timeout,
    )
    content = resp.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
    return content

