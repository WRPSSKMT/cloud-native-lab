# 云原生技术综合实验：计数器微服务

## 1. 应用说明

Flask 提供 `/`、`/api`、`/health` 三个接口；Redis 保存计数值。响应中的 `pod` 字段返回当前容器/Pod 的主机名，可用于观察请求被不同副本处理的情况。

- `GET /`：返回 HTML 页面，显示当前 Pod 名与访问次数
- `GET /api`：返回 JSON，含 `pod` 与 `visits` 字段
- `GET /health`：健康检查，返回 ok

## 2. 环境要求

- Windows 11 + WSL2
- Docker Desktop（已启用 WSL2 backend）
- Docker Desktop 内置 Kubernetes（kind 驱动）
- kubectl v1.36.1

> 注：本次实验最初尝试 Minikube，但因国内网络无法访问 gcr.io / registry.k8s.io，多次重试失败，最终改用 Docker Desktop 内置 Kubernetes。该集群与 Docker 共享镜像存储，无需 `minikube image load`。

## 3. 项目结构

```
.
├── src/
│   ├── app.py
│   └── requirements.txt
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── k8s/
│   └── all.yaml
├── screenshots/
└── README.md
```

## 4. Docker Compose 运行

在项目根目录执行：

```powershell
docker build -t myapp:1.0 -f docker/Dockerfile .
docker compose -f docker/docker-compose.yml up -d --build
docker compose -f docker/docker-compose.yml ps
curl.exe http://localhost:8000/api
curl.exe http://localhost:8000/api
curl.exe http://localhost:8000/api
docker stats --no-stream
```

预期：api 与 redis 容器均 running；三次 curl 返回 `visits` 依次递增。

停止：

```powershell
docker compose -f docker/docker-compose.yml down
```

## 5. Kubernetes 运行

### 5.1 启用 Docker Desktop Kubernetes

1. Docker Desktop → Settings → Kubernetes
2. 勾选 **Enable Kubernetes**，点 **Apply & Restart**
3. 等左下角出现绿色 Kubernetes 图标

### 5.2 部署

```powershell
kubectl config use-context docker-desktop
kubectl get nodes
kubectl apply -f k8s/all.yaml
kubectl get pods,svc
```

预期：2 个 api Pod + 1 个 redis Pod 均为 Running。

### 5.3 访问应用

```powershell
kubectl port-forward svc/api 8080:5000
```

另开 PowerShell 窗口：

```powershell
curl.exe http://localhost:8080/api
curl.exe http://localhost:8080/api
curl.exe http://localhost:8080/api
```

## 6. 自愈验证

开一个窗口持续访问：

```powershell
while ($true) { curl.exe -s http://localhost:8080/api; Start-Sleep 1 }
```

另开窗口删除 Pod：

```powershell
kubectl get pods
kubectl delete pod <替换为一个 api 的真实 Pod 名称>
kubectl get pods -w
```

观察旧 Pod 终止、新 Pod 自动创建并进入 Running。持续访问窗口的 visits 应保持递增，未中断。

## 7. 扩缩容验证

```powershell
kubectl scale deployment api --replicas=5
kubectl get pods
kubectl scale deployment api --replicas=2
kubectl get pods
```

记录扩缩容前后 Pod 数量。若 `kubectl top pods` 提示 Metrics API 不可用，则在报告中如实说明未采集到资源指标。

## 8. 注意

- 任何实验数值、运行时间、资源占用和问题分析都应根据本机实测填写。
- Kubernetes Secret 默认是 Base64 编码而非自动加密，生产环境需另行配置加密与权限控制。
- 跨平台消融（虚拟机 vs 容器）部分因时间限制未完成，报告中已如实说明。