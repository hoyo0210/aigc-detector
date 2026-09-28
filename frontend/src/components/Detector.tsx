import { useState } from 'react';
import { Button, Input, Card, Alert, Progress, Typography, Tag, Grid } from 'antd';
import axios from 'axios';
import { DetectResult } from '../types';

const { TextArea } = Input;
const { Title, Text } = Typography;
const { useBreakpoint } = Grid;

// 最小文本长度限制
const MIN_TEXT_LENGTH = 500;

// 计算文本长度（中文字符数）
const getTextLength = (text: string): number => {
  return text.trim().length;
};

export default function Detector() {
  const screens = useBreakpoint();
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DetectResult | null>(null);
  const [error, setError] = useState('');

  const onDetect = async () => {
    const textLength = getTextLength(text);
    if (textLength < MIN_TEXT_LENGTH) {
      setError(`文本长度不足，至少需要 ${MIN_TEXT_LENGTH} 字，当前 ${textLength} 字`);
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    try {
      const resp = await axios.post('/api/detect', { text });
      setResult(resp.data.result);
    } catch (e: any) {
      setError(e?.response?.data?.detail || '请求失败');
    } finally {
      setLoading(false);
    }
  };

  const getLabelColor = (label: string) => {
    switch (label) {
      case 'human':
        return '#52c41a';
      case 'ai':
        return '#ff4d4f';
      case 'uncertain':
        return '#faad14';
      default:
        return '#d9d9d9';
    }
  };

  const getLabelText = (label: string) => {
    switch (label) {
      case 'human':
        return '人类';
      case 'ai':
        return 'AI';
      case 'uncertain':
        return '不确定';
      default:
        return '未知';
    }
  };

  const getConfidenceText = (confidence: string) => {
    const confidenceMap: { [key: string]: string } = {
      'high': '高',
      'medium': '中',
      'low': '低'
    };
    return confidenceMap[confidence] || confidence;
  };

  const getConfidenceColor = (confidence: string) => {
    const colorMap: { [key: string]: string } = {
      'high': 'green',
      'medium': 'orange',
      'low': 'red'
    };
    return colorMap[confidence] || 'default';
  };

  const textLength = getTextLength(text);
  const isTextValid = textLength >= MIN_TEXT_LENGTH;

  return (
    <Card title="文本检测">
      <TextArea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={screens.xs ? 8 : screens.sm ? 9 : 10}
        placeholder="请输入要检测的文本（至少500字）..."
        style={{
          marginBottom: 8,
          fontSize: screens.xs ? '14px' : '16px'
        }}
      />
      <div style={{
        marginBottom: 16,
        fontSize: screens.xs ? '12px' : '14px',
        color: isTextValid ? '#52c41a' : '#ff4d4f',
        textAlign: 'right'
      }}>
        字数：{textLength} / {MIN_TEXT_LENGTH}
        {!isTextValid && textLength > 0 && (
          <span style={{ marginLeft: 8 }}>
            （还需 {MIN_TEXT_LENGTH - textLength} 字）
          </span>
        )}
      </div>
      <Button
        type="primary"
        onClick={onDetect}
        loading={loading}
        disabled={!text.trim() || !isTextValid}
        block
        size={screens.xs ? 'middle' : 'large'}
        style={{
          fontSize: screens.xs ? '14px' : '16px',
          height: screens.xs ? '40px' : 'auto'
        }}
      >
        {loading ? '检测中...' : '开始检测'}
      </Button>
      {error && (
        <Alert
          message="错误"
          description={error}
          type="error"
          showIcon
          style={{ marginTop: 16 }}
        />
      )}
      {result && (
        <Card
          style={{ marginTop: 16 }}
          bordered={false}
          styles={{ body: { padding: '16px' } }}
        >
          <Title level={4}>检测结果</Title>

          {/* 基本结果 */}
          <div style={{
            display: 'flex',
            flexDirection: screens.xs ? 'column' : 'row',
            alignItems: screens.xs ? 'stretch' : 'center',
            gap: screens.xs ? '12px' : '16px',
            marginBottom: '16px'
          }}>
            <div>
              <Text strong style={{
                color: getLabelColor(result.label),
                fontSize: screens.xs ? '14px' : '16px'
              }}>
                标签: {getLabelText(result.label)}
              </Text>
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              flexWrap: 'wrap'
            }}>
              <Text style={{ fontSize: screens.xs ? '14px' : '16px' }}>
                {result.label === 'human' ? '人类写作概率: ' : result.label === 'ai' ? 'AI生成概率: ' : '置信度: '}
              </Text>
              <Progress
                percent={
                  result.label === 'human' 
                    ? (1 - result.score) * 100  // 人类写作概率
                    : result.label === 'ai'
                    ? result.score * 100  // AI生成概率
                    : Math.abs(result.score - 0.5) * 200  // 不确定时显示偏离中值的程度
                }
                status="active"
                showInfo={false}
                strokeColor={getLabelColor(result.label)}
                style={{
                  width: screens.xs ? '100px' : '120px',
                  marginRight: '8px'
                }}
              />
              <Text style={{ fontSize: screens.xs ? '14px' : '16px' }}>
                {result.label === 'human'
                  ? `${((1 - result.score) * 100).toFixed(1)}%`
                  : result.label === 'ai'
                  ? `${(result.score * 100).toFixed(1)}%`
                  : `${(result.score * 100).toFixed(1)}%`}
              </Text>
            </div>
            <div>
              <Text style={{ fontSize: screens.xs ? '14px' : '16px' }}>判断置信度: </Text>
              <Tag
                color={getConfidenceColor(result.confidence)}
                style={{ fontSize: screens.xs ? '12px' : '14px' }}
              >
                {getConfidenceText(result.confidence)}
              </Tag>
            </div>
          </div>

          {/* 简要解释 */}
          <div style={{ marginBottom: '16px' }}>
            <Text strong>判断理由: </Text>
            <Text>{result.rationale}</Text>
          </div>

          {/* 详细分析 */}
          {result.detailed_analysis && (
            <div style={{ marginBottom: '16px' }}>
              <Text strong>详细分析: </Text>
              <div style={{
                backgroundColor: '#f9f9f9',
                padding: '12px',
                borderRadius: '4px',
                marginTop: '8px',
                whiteSpace: 'pre-wrap',
                lineHeight: '1.6'
              }}>
                {result.detailed_analysis}
              </div>
            </div>
          )}

          {/* 关键指标 */}
          {result.key_indicators && result.key_indicators.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <Text strong>关键指标: </Text>
              <div style={{ marginTop: '8px' }}>
                {result.key_indicators.map((indicator, index) => (
                  <Tag key={index} style={{ marginBottom: '4px', marginRight: '8px' }}>
                    {indicator}
                  </Tag>
                ))}
              </div>
            </div>
          )}

          {/* 判断方法 */}
          {result.methodology && (
            <div>
              <Text strong>判断方法: </Text>
              <div style={{
                backgroundColor: '#f0f8ff',
                padding: '8px 12px',
                borderRadius: '4px',
                marginTop: '4px',
                fontSize: '12px',
                color: '#666'
              }}>
                {result.methodology}
              </div>
            </div>
          )}
        </Card>
      )}
    </Card>
  );
}
