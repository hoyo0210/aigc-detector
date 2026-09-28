import json
from typing import Dict, List
from app.qwen_client import detect_with_qwen, detect_sentence_with_context
from app.text_preprocessor import preprocess_text, split_into_sentences, extract_text_features
from app.config import settings


def parse_model_response(raw: str) -> Dict:
    """
    解析模型返回的JSON响应
    """
    try:
        # 清理和提取JSON
        cleaned_raw = raw.strip()

        # 移除可能的markdown代码块标记
        if cleaned_raw.startswith('```json'):
            cleaned_raw = cleaned_raw[7:]
        if cleaned_raw.startswith('```'):
            cleaned_raw = cleaned_raw[3:]
        if cleaned_raw.endswith('```'):
            cleaned_raw = cleaned_raw[:-3]

        cleaned_raw = cleaned_raw.strip()

        # 确保以{开头，以}结尾
        if not cleaned_raw.startswith('{'):
            start_idx = cleaned_raw.find('{')
            if start_idx != -1:
                cleaned_raw = cleaned_raw[start_idx:]

        if not cleaned_raw.endswith('}'):
            end_idx = cleaned_raw.rfind('}')
            if end_idx != -1:
                cleaned_raw = cleaned_raw[:end_idx+1]

        # 解析JSON
        data = json.loads(cleaned_raw)
        return data
    except Exception as e:
        raise ValueError(f"JSON解析失败: {str(e)}")


def detect_document_level(text: str) -> Dict:
    """
    文档级检测：对整篇文本进行整体分析
    """
    # 预处理文本
    processed_text = preprocess_text(text)
    
    # 调用模型
    raw = detect_with_qwen(processed_text, granularity="document")
    
    # 解析响应
    data = parse_model_response(raw)
    
    # 验证并清理数据
    label = str(data.get("label", "uncertain")).strip()
    if label not in ["ai", "human", "uncertain"]:
        label = "uncertain"

    score = float(data.get("score", 0.5))
    score = max(0.0, min(1.0, score))

    confidence = str(data.get("confidence", "medium")).strip()
    if confidence not in ["high", "medium", "low"]:
        confidence = "medium"

    rationale = str(data.get("rationale", "")).strip()
    detailed_analysis = str(data.get("detailed_analysis", "")).strip()

    key_indicators = data.get("key_indicators", [])
    if not isinstance(key_indicators, list):
        key_indicators = [str(key_indicators)]
    key_indicators = [str(item).strip() for item in key_indicators if str(item).strip()]

    methodology = str(data.get("methodology", "基于多维度特征分析的AI检测算法")).strip()
    
    return {
        "label": label,
        "score": score,
        "confidence": confidence,
        "rationale": rationale,
        "detailed_analysis": detailed_analysis,
        "key_indicators": key_indicators,
        "methodology": methodology
    }


def detect_sentence_level(text: str, suspicious_sentences: List[str] = None) -> Dict:
    """
    句子级检测：对可疑句子进行精细分析
    
    Args:
        text: 完整文本
        suspicious_sentences: 可疑句子列表，如果为None则自动选择
    """
    sentences = split_into_sentences(text)
    
    if not sentences:
        return {
            "suspicious_sentences": [],
            "sentence_analysis": [],
            "enhanced_confidence": "medium"
        }
    
    # 如果没有指定可疑句子，选择前3-5个句子进行分析
    if suspicious_sentences is None:
        # 简单策略：选择前几个句子
        num_to_analyze = min(5, len(sentences))
        suspicious_sentences = sentences[:num_to_analyze]
    
    sentence_results = []
    ai_sentence_count = 0
    
    for sentence in suspicious_sentences:
        try:
            # 构建上下文（前后各一个句子）
            sentence_idx = sentences.index(sentence) if sentence in sentences else 0
            context_start = max(0, sentence_idx - 1)
            context_end = min(len(sentences), sentence_idx + 2)
            context = " ".join(sentences[context_start:context_end])
            
            # 调用句子级检测
            raw = detect_sentence_with_context(sentence, context)
            data = parse_model_response(raw)
            
            is_ai_likely = data.get("is_ai_likely", False)
            if is_ai_likely:
                ai_sentence_count += 1
            
            sentence_results.append({
                "sentence": sentence,
                "is_ai_likely": is_ai_likely,
                "confidence": data.get("confidence", "medium"),
                "reason": data.get("reason", ""),
                "indicators": data.get("indicators", [])
            })
        except Exception as e:
            # 如果句子级检测失败，跳过该句子
            continue
    
    # 根据句子级分析结果调整置信度
    ai_ratio = ai_sentence_count / len(sentence_results) if sentence_results else 0
    if ai_ratio >= 0.7:
        enhanced_confidence = "high"
    elif ai_ratio >= 0.4:
        enhanced_confidence = "medium"
    else:
        enhanced_confidence = "low"
    
    return {
        "suspicious_sentences": suspicious_sentences,
        "sentence_analysis": sentence_results,
        "ai_sentence_ratio": round(ai_ratio, 2),
        "enhanced_confidence": enhanced_confidence
    }


def detect(text: str):
    """
    多粒度检测：结合文档级和句子级分析
    """
    # 提取文本特征（用于辅助判断）
    features = extract_text_features(text)
    
    try:
        # 阶段一：文档级检测
        doc_result = detect_document_level(text)
        
        # 多粒度检测策略
        sentence_result = None
        if settings.enable_multi_granularity:
            should_analyze_sentences = False
            
            # 策略1：如果文档级得分较高（可能是AI），进行句子级精细分析
            if doc_result["score"] >= settings.sentence_analysis_threshold:
                should_analyze_sentences = True
            
            # 策略2：反向检测 - 如果判断为"人类"但置信度不高，也进行句子级验证
            if (settings.enable_reverse_check and 
                doc_result["label"] == "human" and 
                doc_result["confidence"] in ["medium", "low"]):
                should_analyze_sentences = True
            
            if should_analyze_sentences:
                try:
                    sentence_result = detect_sentence_level(text)
                    
                    # 集成两个阶段的结果
                    ai_sentence_ratio = sentence_result.get("ai_sentence_ratio", 0)
                    
                    # 如果句子级分析显示AI特征
                    if ai_sentence_ratio > 0.4:  # 降低阈值，更敏感地检测AI特征
                        # 如果文档级判断为人类，但句子级显示AI特征，需要修正
                        if doc_result["label"] == "human":
                            # 根据句子级分析结果调整
                            if ai_sentence_ratio > 0.6:
                                # 强烈AI特征，修正为AI或不确定
                                doc_result["label"] = "ai"
                                doc_result["score"] = min(0.7, doc_result["score"] + 0.3)
                            else:
                                # 中等AI特征，改为不确定
                                doc_result["label"] = "uncertain"
                                doc_result["score"] = min(0.6, doc_result["score"] + 0.2)
                        
                        # 提升置信度
                        if doc_result["confidence"] == "medium":
                            doc_result["confidence"] = "high"
                        elif doc_result["confidence"] == "low":
                            doc_result["confidence"] = "medium"
                        
                        # 更新方法论说明
                        doc_result["methodology"] = (
                            f"{doc_result['methodology']} "
                            f"结合句子级精细分析，发现{ai_sentence_ratio*100:.0f}%的句子表现出AI特征。"
                        )
                        
                        # 添加句子级的关键指标
                        sentence_indicators = []
                        for analysis in sentence_result.get("sentence_analysis", []):
                            if analysis.get("is_ai_likely", False):
                                sentence_indicators.extend(analysis.get("indicators", []))
                        
                        if sentence_indicators:
                            doc_result["key_indicators"].extend(sentence_indicators[:3])  # 最多添加3个
                            doc_result["key_indicators"] = list(set(doc_result["key_indicators"]))  # 去重
                except Exception as e:
                    # 句子级检测失败不影响整体结果
                    pass
        
        return doc_result
        
    except Exception as e:
        # 如果所有解析都失败，返回标准错误响应
        return {
            "label": "uncertain",
            "score": 0.5,
            "confidence": "low",
            "rationale": f"检测失败: {str(e)[:100]}",
            "detailed_analysis": "由于AI模型返回格式不符合要求，无法提供详细分析。",
            "key_indicators": ["格式解析失败"],
            "methodology": "基础模式匹配"
        }

    try:
        # 清理和提取JSON
        cleaned_raw = raw.strip()

        # 移除可能的markdown代码块标记
        if cleaned_raw.startswith('```json'):
            cleaned_raw = cleaned_raw[7:]
        if cleaned_raw.startswith('```'):
            cleaned_raw = cleaned_raw[3:]
        if cleaned_raw.endswith('```'):
            cleaned_raw = cleaned_raw[:-3]

        cleaned_raw = cleaned_raw.strip()

        # 确保以{开头，以}结尾
        if not cleaned_raw.startswith('{'):
            start_idx = cleaned_raw.find('{')
            if start_idx != -1:
                cleaned_raw = cleaned_raw[start_idx:]

        if not cleaned_raw.endswith('}'):
            end_idx = cleaned_raw.rfind('}')
            if end_idx != -1:
                cleaned_raw = cleaned_raw[:end_idx+1]

        # 解析JSON
        data = json.loads(cleaned_raw)

        # 验证必需字段
        required_fields = ["label", "score"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必需字段: {field}")

        # 验证并清理数据
        label = str(data.get("label", "uncertain")).strip()
        if label not in ["ai", "human", "uncertain"]:
            label = "uncertain"

        score = float(data.get("score", 0.5))
        score = max(0.0, min(1.0, score))  # 确保在0-1范围内

        confidence = str(data.get("confidence", "medium")).strip()
        if confidence not in ["high", "medium", "low"]:
            confidence = "medium"

        rationale = str(data.get("rationale", "")).strip()
        detailed_analysis = str(data.get("detailed_analysis", "")).strip()

        key_indicators = data.get("key_indicators", [])
        if not isinstance(key_indicators, list):
            key_indicators = [str(key_indicators)]
        key_indicators = [str(item).strip() for item in key_indicators if str(item).strip()]

        methodology = str(data.get("methodology", "基于多维度特征分析的AI检测算法")).strip()

        return {
            "label": label,
            "score": score,
            "confidence": confidence,
            "rationale": rationale,
            "detailed_analysis": detailed_analysis,
            "key_indicators": key_indicators,
            "methodology": methodology
        }

    except Exception as e:
        # 如果所有解析都失败，返回标准错误响应
        return {
            "label": "uncertain",
            "score": 0.5,
            "confidence": "low",
            "rationale": f"检测失败: {str(e)[:100]}",
            "detailed_analysis": "由于AI模型返回格式不符合要求，无法提供详细分析。",
            "key_indicators": ["格式解析失败"],
            "methodology": "基础模式匹配"
        }
