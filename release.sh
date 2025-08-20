#!/bin/bash
git pull
docker build -t tiny-comics:latest .
kubectl get pods -l app=comics -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.status.containerStatuses[0].imageID}{"\n"}{end}'
k3d image import tiny-comics:latest -c njord-cluster
kubectl rollout restart deploy/comics
kubectl rollout status deploy/comics
kubectl get pods -l app=comics -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.status.containerStatuses[0].imageID}{"\n"}{end}'
docker ps --format '{{.Names}}' | grep k3d-

# Prune dangling/unused images in all k3d nodes
for node in $(docker ps --format '{{.Names}}' | grep k3d-); do
    echo "Pruning images in $node..."
    docker exec $node crictl rmi --prune || docker exec $node nerdctl image prune -f
done

