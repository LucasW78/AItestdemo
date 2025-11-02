# 🌐 AI测试用例生成平台 - 外网访问配置

## 📋 访问信息

### 🌍 外网访问地址
- **前端应用**: http://47.101.190.42:3000
- **后端API**: http://47.101.190.42:8000
- **API文档**: http://47.101.190.42:8000/docs
- **健康检查**: http://47.101.190.42:8000/health

### 🏠 本地访问地址
- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 🔧 网络配置

### 服务器信息
- **外网IP**: 47.101.190.42
- **内网IP**: 172.24.53.221
- **操作系统**: AliLinux
- **防火墙状态**: 关闭
- **端口状态**: 开放

### 开放端口
- **3000**: 前端Web服务
- **8000**: 后端API服务

## 🛠️ 服务管理

### 查看运行状态
```bash
# 查看端口占用
netstat -tlnp | grep -E ':(3000|8000)'

# 查看进程
ps aux | grep -E '(simple_backend|http.server)'

# 检查服务健康状态
curl http://localhost:8000/health
```

### 启动服务
```bash
# 启动后端服务
cd /opt/AItestdemo
python3 simple_backend.py &

# 启动前端服务
cd frontend/dist
python3 -m http.server 3000 --bind 0.0.0.0 &
```

### 停止服务
```bash
# 查找并停止进程
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

## 🔒 安全注意事项

### 生产环境建议
1. **启用防火墙**: 配置iptables或firewalld只允许必要的端口
2. **使用HTTPS**: 配置SSL证书启用HTTPS
3. **域名配置**: 使用域名代替IP地址访问
4. **访问控制**: 添加用户认证和访问限制
5. **监控日志**: 配置日志监控和异常告警

### 当前安全配置
- 防火墙关闭（仅用于演示）
- HTTP协议（未加密传输）
- 无访问认证
- 数据存储在内存中

## 🌐 客户端访问

### 浏览器访问
1. 打开浏览器
2. 访问: http://47.101.190.42:3000
3. 开始使用AI测试用例生成平台

### API访问
```bash
# 测试API连接
curl http://47.101.190.42:8000/health

# 生成测试用例
curl -X POST http://47.101.190.42:8000/api/v1/testcases/generate \
  -H "Content-Type: application/json" \
  -d '{"content":"测试登录功能","test_type":"functional"}'

# 上传文档
curl -X POST http://47.101.190.42:8000/api/v1/documents/upload \
  -F "file=@test.txt"
```

## 📱 移动端访问

手机或平板设备可以通过浏览器直接访问外网地址：
http://47.101.190.42:3000

## 🚨 故障排除

### 无法访问？
1. 检查服务器服务是否正常运行
2. 确认端口3000和8000没有被其他程序占用
3. 检查云服务商安全组配置
4. 验证防火墙设置

### 服务异常重启？
```bash
# 重启所有服务
cd /opt/AItestdemo
kill $(lsof -ti:3000) $(lsof -ti:8000)
python3 simple_backend.py &
cd frontend/dist && python3 -m http.server 3000 --bind 0.0.0.0 &
```

## 📞 技术支持

如遇到问题，请检查：
1. 服务器网络连接
2. 服务进程状态
3. 端口占用情况
4. 防火墙配置

---

**注意**: 当前配置为演示环境，生产环境请使用HTTPS和更完善的安全配置。