#!/bin/bash
git pull
docker build -t tiny-comics:latest .
kubectl get pods -l app=comics -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.status.containerStatuses[0].imageID}{"\n"}{end}'
k3d image import tiny-comics:latest -c njord-cluster
kubectl rollout restart deploy/comics
kubectl rollout status deploy/comics
kubectl get pods -l app=comics -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.status.containerStatuses[0].imageID}{"\n"}{end}'

