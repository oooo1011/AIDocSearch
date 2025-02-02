import React from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const onFinish = async (values) => {
    try {
      const formData = new FormData();
      formData.append('username', values.email);
      formData.append('password', values.password);

      const response = await axios.post('http://localhost:8000/token', formData);
      login(response.data.access_token);
      message.success('登录成功');
      navigate('/');
    } catch (error) {
      message.error('登录失败: ' + (error.response?.data?.detail || '未知错误'));
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '100px auto', padding: '0 20px' }}>
      <Card title="登录" bordered={false}>
        <Form
          name="login"
          onFinish={onFinish}
          layout="vertical"
        >
          <Form.Item
            name="email"
            label="邮箱"
            rules={[{ required: true, message: '请输入邮箱' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="password"
            label="密码"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              登录
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            还没有账号？ <Link to="/register">注册</Link>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default Login;
