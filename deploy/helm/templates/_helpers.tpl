{{/*
CatWiki Helm Chart - 通用模板辅助函数
*/}}

{{/*
Chart 全名
*/}}
{{- define "catwiki.fullname" -}}
{{- default .Chart.Name .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Chart 名称
*/}}
{{- define "catwiki.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
通用标签
*/}}
{{- define "catwiki.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: catwiki
{{- end }}

{{/*
组件标签
*/}}
{{- define "catwiki.selectorLabels" -}}
app.kubernetes.io/name: {{ include "catwiki.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
镜像地址辅助函数
*/}}
{{- define "catwiki.image" -}}
{{- $registry := .global.imageRegistry | default "" -}}
{{- if $registry -}}
{{- printf "%s/%s:%s" $registry .image.repository .image.tag -}}
{{- else -}}
{{- printf "%s:%s" .image.repository .image.tag -}}
{{- end -}}
{{- end }}
