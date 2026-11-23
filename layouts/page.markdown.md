{{- /*
  Clean Markdown twin of each page for AI agents / answer engines.
  Bundle images are rewritten to absolute URLs of a web-sized copy.
*/ -}}
{{- $md := .RenderShortcodes | string -}}
{{- range .Resources.ByType "image" -}}
  {{- $r := . -}}
  {{- if and (reflect.IsImageResourceProcessable .) (ne .MediaType.SubType "gif") (gt .Width 1280) }}{{ $r = .Resize "1280x" }}{{ end -}}
  {{- $md = replace $md (printf "](%s" .Name) (printf "](%s" $r.Permalink) -}}
{{- end -}}
---
title: {{ .Title | jsonify }}
url: {{ with .OutputFormats.Get "html" }}{{ .Permalink }}{{ end }}
{{- with .Description }}
description: {{ . | jsonify }}
{{- end }}
{{- if .IsPage }}
published: {{ .PublishDate.Format "2006-01-02" }}
updated: {{ .Lastmod.Format "2006-01-02" }}
{{- end }}
{{- with .GetTerms "authors" }}
author: {{ (index . 0).LinkTitle | jsonify }}
{{- end }}
{{- with .Params.interviewee }}
interviewee: {{ .name | jsonify }}
{{- end }}
---

# {{ .Title }}

{{ $md | strings.TrimSpace }}
