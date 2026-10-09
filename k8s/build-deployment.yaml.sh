#!/bin/sh
# Generates deployment.yaml from environment variables provided by the CI/CD pipeline.
# No secrets are stored here: every sensitive value is an env placeholder injected at deploy
# time from GitHub Actions vars/secrets. Health probes hit the unauthenticated /healthz route.

cat << EOF >> deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${DEPLOYMENT_NAME}
  namespace: ${K8S_NAMESPACE}
spec:
  selector:
    matchLabels:
      app: ${DEPLOYMENT_NAME}
  replicas: 2
  strategy:
    rollingUpdate:
      maxSurge: 100%
      maxUnavailable: 0
    type: RollingUpdate
  minReadySeconds: 5
  template:
    metadata:
      labels:
        app: ${DEPLOYMENT_NAME}
    spec:
      containers:
      - name: ${DEPLOYMENT_NAME}
        image: ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
        env:
          - name: MCP_API_KEY
            value: "${MCP_API_KEY}"
          - name: KEYCLOAK_API_HOST
            value: "${KEYCLOAK_API_HOST}"
          - name: KEYCLOAK_CLIENT_ID
            value: "${KEYCLOAK_CLIENT_ID}"
          - name: KEYCLOAK_CLIENT_SECRET
            value: "${KEYCLOAK_CLIENT_SECRET}"
          - name: IA_API_HOST
            value: "${IA_API_HOST}"
          - name: QDRANT_HOST
            value: "${QDRANT_HOST}"
          - name: QDRANT_PORT
            value: "${QDRANT_PORT}"
          - name: QDRANT_API_KEY
            value: "${QDRANT_API_KEY}"
          - name: QDRANT_COLLECTION_NAME
            value: "${QDRANT_COLLECTION_NAME}"
          - name: GITHUB_APP_ID
            value: "${GH_APP_ID}"
          - name: GITHUB_APP_INSTALLATION_ID
            value: "${GH_APP_INSTALLATION_ID}"
          - name: GITHUB_APP_PRIVATE_KEY
            value: "${GH_APP_PRIVATE_KEY}"
          - name: REDIS_HOST
            value: "${REDIS_HOST}"
          - name: REDIS_PORT
            value: "${REDIS_PORT}"
          - name: REDIS_DB
            value: "${REDIS_DB}"
        readinessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 20
        resources:
          limits:
            memory: 1Gi
          requests:
            cpu: 150m
            memory: 1Gi
---
apiVersion: v1
kind: Service
metadata:
  name: ${DEPLOYMENT_NAME}
  namespace: ${K8S_NAMESPACE}
spec:
  selector:
    app: ${DEPLOYMENT_NAME}
  ports:
  - protocol: TCP
    name: http
    port: 8000
    targetPort: 8000
  type: ClusterIP
EOF
