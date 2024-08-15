{{- define "resc.webServiceServiceTemplate" -}}
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.global.appName }}-api{{ .Values.nameSuffix }}
  namespace: {{ .Values.global.namespace }}
  labels:
    app: {{ .Values.global.appName }}
    tier: api{{ .Values.nameSuffix }}
  annotations:
    datree.skip/SERVICE_INCORRECT_TYPE_VALUE_NODEPORT: irrelevant as its only exposed for local environment and can be enabled/disabled from env specific values.yaml
    {{- if and .Values.service .Values.service.annotations }}
    {{- toYaml .Values.service.annotations | nindent 4 }}
    {{- end }}
spec:
  {{ if .Values.exposeToHostPort }}
  type: NodePort
  {{ end }}
  ports:
    - port: {{ .Values.port }}
      targetPort: {{ .Values.port }}
      {{ if .Values.exposeToHostPort }}
      nodePort: {{ .Values.exposeToHostPort }}
      {{ end }}
  selector:
    app: {{ .Values.global.appName }}
    tier: api{{ .Values.nameSuffix }}
{{- end }}