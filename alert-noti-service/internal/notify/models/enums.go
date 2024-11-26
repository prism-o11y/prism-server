package models

type AlertSeverity string

const (
	Critical AlertSeverity = "CRITICAL"
	Warning  AlertSeverity = "WARNING"
	Info     AlertSeverity = "INFO"
)

type Action string

const (
	SSE  Action = "SSE"
	SMTP Action = "SMTP"
)
