{{- define "resc.webServiceServiceTemplate" -}}
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.global.appName }}-api{{ .Values.nameSuffix }}
  namespace: {{ .Values.global.namespace }}
  labels:
    app: {{ .Values.global.appName }}
    tier: api{{ .Values.nameSuffix }}
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