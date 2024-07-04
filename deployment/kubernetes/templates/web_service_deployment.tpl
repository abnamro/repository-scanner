{{- define "resc.webServiceDeploymentTemplate" -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.global.appName }}-web-service{{ .Values.nameSuffix }}
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
        {{- with include "resc.rescWebserviceAnnotations" .}}
          {{- nindent 8 .}}
        {{- end }}
        container.apparmor.security.beta.kubernetes.io/resc-api: unconfined
      labels:
        {{ if .Values.additionalLabels }}
        {{- range $key, $val := .Values.additionalLabels }}    
        {{ $key }}: {{ $val | quote }}    
        {{- end}}
        {{ end }}
        app: {{ .Values.global.appName }}
        tier: api{{ .Values.nameSuffix }}
        kubeaudit.io/allow-disabled-apparmor: "apparmor-needs-to-be-installed-on-host"
        kubeaudit.io/allow-read-only-root-filesystem-false: "required-to-write-log-files"
    spec:
      {{ if .Values.global.serviceAccountName }}
      serviceAccountName: {{ .Values.global.serviceAccountName }}
      {{ end }}
      containers:
        - name: {{ .Values.global.appName }}-api
          image: {{ .Values.resc.image.repository | default .Values.global.resc.image.repository }}{{ .Values.resc.image.name | default .Values.global.resc.image.name }}:{{ .Values.resc.image.tag | default .Values.global.resc.image.tag }}
          imagePullPolicy: {{ .Values.resc.image.pullPolicy | default .Values.global.resc.image.pullPolicy }}
          command: ["sh", "-c"]
          args: ["{{ .Values.preStartUpCommand }} cp /tmp/odbc.ini ~/.odbc.ini; uvicorn resc_backend.resc_web_service.api:app --workers {{ .Values.workers }} --host 0.0.0.0 --port {{ .Values.port }} --no-access-log"]
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
                name: {{ .Values.global.appName }}-web-service-config{{ .Values.nameSuffix }}
            - secretRef:
                name: {{ .Values.global.appName }}-web-service-secret
          ports:
            - containerPort: {{ .Values.port }}
          volumeMounts:
            - name: config-volume
              mountPath: /tmp/odbc.ini
              subPath: odbc.ini
            {{- $additionalVolumeMounts := include "resc.rescWebserviceAdditionalVolumeMounts" . }}
            {{- if $additionalVolumeMounts }}
            {{- with include "resc.rescWebserviceAdditionalVolumeMounts" .}}
                {{- nindent 12 .}}
            {{- end }}
            {{- end }}
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: false
            privileged: false
            capabilities:
              drop:
                - ALL
            seccompProfile:
              type: RuntimeDefault
            runAsNonRoot: true
            runAsUser: 10001
          livenessProbe:
            httpGet:
              path: /resc/v1/health
              port: {{ .Values.port }}
            initialDelaySeconds: 20
            periodSeconds: 300
            timeoutSeconds: 30
          readinessProbe:
            httpGet:
              path: /resc/v1/health
              port: {{ .Values.port }}
            initialDelaySeconds: 20
            periodSeconds: 300
            timeoutSeconds: 10
      volumes:
        - name: config-volume
          configMap:
            name: {{ .Values.global.appName }}-web-service-config{{ .Values.nameSuffix }}
        {{- $additionalVolumes := include "resc.rescWebserviceAdditionalVolumes" . }}
        {{- if $additionalVolumes }}
        {{- with include "resc.rescWebserviceAdditionalVolumes" .}}
          {{- nindent 8 .}}
        {{- end }}
        {{- end }}
      {{ if .Values.global.imagePullSecret }}
      imagePullSecrets:
      - name: {{ .Values.global.imagePullSecret }}
      {{ end }}
      {{ if .Values.global.serviceAccountName }}
      automountServiceAccountToken: true
      {{ else }}
      automountServiceAccountToken: false
      {{ end }}
{{- end }}