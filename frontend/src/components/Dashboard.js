import React, { useState, useEffect, useRef } from 'react';
import { Layout, Input, Select, Upload, Button, Card, List, message, Tabs, Spin } from 'antd';
import { UploadOutlined, SearchOutlined, LogoutOutlined } from '@ant-design/icons';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const { Header, Content } = Layout;
const { TextArea } = Input;
const { Option } = Select;

const Dashboard = () => {
  const { token, logout } = useAuth();
  const [query, setQuery] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('deepseek');
  const [selectedModel, setSelectedModel] = useState('');
  const [result, setResult] = useState('');
  const [history, setHistory] = useState({ searches: [], analyses: [] });
  const [models, setModels] = useState({});
  const [loading, setLoading] = useState(false);
  const abortController = useRef(null);

  useEffect(() => {
    fetchModels();
    fetchHistory();
  }, []);

  const fetchModels = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/models', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setModels(response.data);
      // 设置默认模型
      if (response.data.deepseek?.length > 0) {
        setSelectedModel(response.data.deepseek[0]);
      }
    } catch (error) {
      message.error('获取模型列表失败');
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/history', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setHistory(response.data);
    } catch (error) {
      message.error('获取历史记录失败');
    }
  };

  const handleProviderChange = (value) => {
    setSelectedProvider(value);
    // 更新选中的模型为新提供商的第一个可用模型
    if (models[value]?.length > 0) {
      setSelectedModel(models[value][0]);
    } else {
      setSelectedModel('');
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) {
      message.warning('请输入搜索内容');
      return;
    }
    
    setLoading(true);
    setResult('');

    // 取消之前的请求
    if (abortController.current) {
      abortController.current.abort();
    }
    abortController.current = new AbortController();

    try {
      const response = await fetch(
        `http://localhost:8000/api/search/stream?${new URLSearchParams({
          query,
          model: selectedProvider,
          model_name: selectedModel
        })}`,
        {
          headers: { Authorization: `Bearer ${token}` },
          signal: abortController.current.signal
        }
      );

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(5).trim();
            if (data === '[DONE]') {
              break;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.error) {
                message.error(parsed.error);
                break;
              }
              if (parsed.content) {
                setResult(prev => prev + parsed.content);
              }
            } catch (e) {
              console.error('解析响应失败:', e);
            }
          }
        }
      }

      fetchHistory();
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('请求被取消');
      } else {
        message.error('搜索失败: ' + (error.response?.data?.detail || '未知错误'));
      }
    } finally {
      setLoading(false);
      abortController.current = null;
    }
  };

  const handleFileUpload = async (info) => {
    const { file } = info;
    if (!selectedProvider || !selectedModel) {
      message.warning('请选择AI模型');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('model', selectedProvider);
    formData.append('model_name', selectedModel);

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/process-document',
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      setResult(response.data.analysis);
      fetchHistory();
    } catch (error) {
      message.error('文档处理失败: ' + (error.response?.data?.detail || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Header style={{ display: 'flex', justifyContent: 'flex-end', background: '#fff', padding: '0 24px' }}>
        <Button type="link" onClick={logout} icon={<LogoutOutlined />}>
          退出登录
        </Button>
      </Header>
      <Content style={{ padding: '24px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <Card>
            <div style={{ marginBottom: 20 }}>
              <Input.Group compact>
                <Input
                  style={{ width: 'calc(100% - 400px)' }}
                  placeholder="输入搜索关键词"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onPressEnter={handleSearch}
                />
                <Select
                  style={{ width: 150 }}
                  value={selectedProvider}
                  onChange={handleProviderChange}
                >
                  <Option value="deepseek">DeepSeek</Option>
                  <Option value="ollama">Ollama</Option>
                  <Option value="groq">GROQ</Option>
                </Select>
                <Select
                  style={{ width: 150 }}
                  value={selectedModel}
                  onChange={setSelectedModel}
                  disabled={!models[selectedProvider]?.length}
                >
                  {models[selectedProvider]?.map(model => (
                    <Option key={model} value={model}>{model}</Option>
                  ))}
                </Select>
                <Button
                  type="primary"
                  icon={<SearchOutlined />}
                  onClick={handleSearch}
                  loading={loading}
                >
                  搜索
                </Button>
              </Input.Group>
            </div>

            <Upload
              accept=".pdf,.docx,.txt"
              customRequest={handleFileUpload}
              showUploadList={false}
            >
              <Button icon={<UploadOutlined />} loading={loading}>上传文档</Button>
            </Upload>

            {result && (
              <Card style={{ marginTop: 20 }}>
                <TextArea
                  value={result}
                  autoSize={{ minRows: 3, maxRows: 10 }}
                  readOnly
                />
              </Card>
            )}

            <Tabs style={{ marginTop: 20 }}>
              <Tabs.TabPane tab="搜索历史" key="searches">
                <List
                  dataSource={history.searches}
                  renderItem={item => (
                    <List.Item>
                      <Card style={{ width: '100%' }}>
                        <p><strong>查询：</strong>{item.query}</p>
                        <p><strong>结果：</strong>{item.results}</p>
                        <p><strong>模型：</strong>{item.model_used}</p>
                        <p><strong>时间：</strong>{new Date(item.created_at).toLocaleString()}</p>
                      </Card>
                    </List.Item>
                  )}
                />
              </Tabs.TabPane>
              <Tabs.TabPane tab="文档分析历史" key="analyses">
                <List
                  dataSource={history.analyses}
                  renderItem={item => (
                    <List.Item>
                      <Card style={{ width: '100%' }}>
                        <p><strong>文件：</strong>{item.filename}</p>
                        <p><strong>分析：</strong>{item.analysis}</p>
                        <p><strong>模型：</strong>{item.model_used}</p>
                        <p><strong>时间：</strong>{new Date(item.created_at).toLocaleString()}</p>
                      </Card>
                    </List.Item>
                  )}
                />
              </Tabs.TabPane>
            </Tabs>
          </Card>
        </div>
      </Content>
    </Layout>
  );
};

export default Dashboard;
