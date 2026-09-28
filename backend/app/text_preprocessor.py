"""
文本预处理模块
提供文本清洗、规范化、分段等功能
"""
import re
from typing import List, Tuple


def clean_text(text: str) -> str:
    """
    清洗文本：移除多余空白、规范化标点等
    """
    if not text:
        return ""
    
    # 移除多余的空白字符（保留单个空格和换行）
    text = re.sub(r'[ \t]+', ' ', text)  # 多个空格/制表符替换为单个空格
    text = re.sub(r'\n{3,}', '\n\n', text)  # 多个换行替换为最多两个
    
    # 规范化中文标点前后的空格
    text = re.sub(r'\s+([，。！？；：])', r'\1', text)  # 标点前不要空格
    text = re.sub(r'([，。！？；：])\s+', r'\1 ', text)  # 标点后保留一个空格
    
    # 移除行首行尾空白
    text = text.strip()
    
    return text


def normalize_text(text: str) -> str:
    """
    规范化文本：统一格式、处理特殊字符
    """
    if not text:
        return ""
    
    # 统一换行符
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # 移除零宽字符
    text = re.sub(r'[\u200b-\u200f\ufeff]', '', text)
    
    # 规范化引号（可选，根据需求决定是否保留）
    # text = text.replace('"', '"').replace('"', '"')
    # text = text.replace(''', "'").replace(''', "'")
    
    return text


def split_into_sentences(text: str) -> List[str]:
    """
    将文本分割成句子
    支持中文和英文标点
    """
    if not text:
        return []
    
    # 中文和英文句子结束符
    sentence_endings = r'[。！？.!?]'
    
    # 分割句子
    sentences = re.split(sentence_endings, text)
    
    # 清理并过滤空句子
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences


def split_into_paragraphs(text: str) -> List[str]:
    """
    将文本分割成段落
    """
    if not text:
        return []
    
    # 按双换行符分割段落
    paragraphs = re.split(r'\n\s*\n', text)
    
    # 清理并过滤空段落
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    return paragraphs


def split_long_text(text: str, max_length: int = 2000) -> List[Tuple[int, int, str]]:
    """
    将长文本分割成多个片段
    返回: [(start_idx, end_idx, segment), ...]
    """
    if len(text) <= max_length:
        return [(0, len(text), text)]
    
    segments = []
    start = 0
    
    # 尝试在句子边界处分割
    sentences = split_into_sentences(text)
    current_segment = ""
    segment_start = 0
    
    for sentence in sentences:
        # 如果加上当前句子会超过长度限制
        if len(current_segment) + len(sentence) + 1 > max_length and current_segment:
            # 保存当前片段
            segments.append((segment_start, segment_start + len(current_segment), current_segment.strip()))
            segment_start = segment_start + len(current_segment)
            current_segment = sentence
        else:
            # 添加句子到当前片段
            if current_segment:
                current_segment += "。" + sentence
            else:
                current_segment = sentence
    
    # 添加最后一个片段
    if current_segment:
        segments.append((segment_start, segment_start + len(current_segment), current_segment.strip()))
    
    return segments


def preprocess_text(text: str) -> str:
    """
    完整的文本预处理流程
    """
    # 1. 规范化
    text = normalize_text(text)
    
    # 2. 清洗
    text = clean_text(text)
    
    return text


def extract_text_features(text: str) -> dict:
    """
    提取文本特征，用于辅助检测
    """
    if not text:
        return {}
    
    # 基本统计
    char_count = len(text)
    word_count = len(text.split()) if text.split() else 0
    sentence_count = len(split_into_sentences(text))
    paragraph_count = len(split_into_paragraphs(text))
    
    # 计算平均句子长度
    sentences = split_into_sentences(text)
    avg_sentence_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0
    
    # 计算平均段落长度
    paragraphs = split_into_paragraphs(text)
    avg_paragraph_length = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0
    
    # 检测正式表达模式
    formal_patterns = [
        r'因此[，,]', r'此外[，,]', r'综上所述[，,]', r'总而言之[，,]',
        r'值得注意的是[，,]', r'需要强调的是[，,]', r'根据以上[，,]'
    ]
    formal_count = sum(len(re.findall(pattern, text)) for pattern in formal_patterns)
    
    # 检测重复词语（简单统计）
    words = text.split()
    word_freq = {}
    for word in words:
        if len(word) > 1:  # 只考虑长度>1的词
            word_freq[word] = word_freq.get(word, 0) + 1
    
    repetition_count = sum(1 for count in word_freq.values() if count >= 3)
    
    return {
        "char_count": char_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "avg_sentence_length": round(avg_sentence_length, 2),
        "avg_paragraph_length": round(avg_paragraph_length, 2),
        "formal_expression_count": formal_count,
        "repetition_count": repetition_count
    }

