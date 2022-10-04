{{- define "resc.stsDeploymentTemplate" -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.global.appName }}-secret-tracking-service{{ .Values.nameSuffix }}
  namespace: {{ .Values.global.namespace }}
spec:
  replicas: {{ .Values.replicas}}
  selector:
    matchLabels:
      app: {{ .Values.global.appName }}
      tier: api{{ .Values.nameSuffix }}
  template:
    metadata:
      annotations:
        rollme: {{ randAlphaNum 5 | quote }}
      labels:
        {{ if .Values.additionalLabels }}
        {{- range $key, $val := .Values.additionalLabels }}    
        {{ $key }}: {{ $val | quote }}    
        {{- end}}
        {{ end }}
        app: {{ .Values.global.appName }}
        tier: api{{ .Values.nameSuffix }}
    spec:
      {{ if .Values.global.serviceAccountName }}
      serviceAccountName: {{ .Values.global.serviceAccountName }}
      {{ end }}
      containers:
        - name: {{ .Values.global.appName }}-api
          image: {{ .Values.resc.image.repository | default .Values.global.resc.image.repository }}{{ .Values.resc.image.name | default .Values.global.resc.image.name }}:{{ .Values.resc.image.tag | default .Values.global.resc.image.tag }}
          imagePullPolicy: {{ .Values.resc.image.pullPolicy | default .Values.global.resc.image.pullPolicy }}
          command: ["sh", "-c"]
          args: ["{{ .Values.preStartUpCommand }} cp /tmp/odbc.ini ~/.odbc.ini; uvicorn repository_scanner_backend.resc_web_service.api:app --workers {{ .Values.workers }} --host 0.0.0.0 --port {{ .Values.port }}"]
          resources:
            requests:
              cpu: {{ .Values.resources.requests.cpu }}
              memory: {{ .Values.resources.requests.memory }}
            limits:
              cpu: {{ .Values.resources.limits.cpu }}
              memory: {{ .Values.resources.limits.memory }}
          env:
            - name: GET_HOSTS_FROM
              value: dns
          envFrom:
            - configMapRef:
                name: {{ .Values.global.appName }}-sts-config{{ .Values.nameSuffix }}
            - secretRef:
                name: {{ .Values.global.appName }}-sts-secret
          ports:
            - containerPort: {{ .Values.port }}
          volumeMounts:
            - name: config-volume
              mountPath: /tmp/odbc.ini
              subPath: odbc.ini
      volumes:
        - name: config-volume
          configMap:
            name: {{ .Values.global.appName }}-sts-config{{ .Values.nameSuffix }}
      {{ if .Values.global.imagePullSecret }}
      imagePullSecrets:
      - name: {{ .Values.global.imagePullSecret }}
      {{ end }}
{{- end }}