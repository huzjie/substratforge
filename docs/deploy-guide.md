# 部署指南

## Docker

```bash
docker build -t substratforge .
docker compose up -d
```

## Kubernetes

```bash
kubectl apply -f deploy/k8s/deployment.yaml
kubectl apply -f deploy/k8s/service.yaml
```

## systemd

```bash
cp deploy/systemd/substratforge.service /etc/systemd/system/
systemctl enable --now substratforge
```
