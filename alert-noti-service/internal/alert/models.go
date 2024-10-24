package alert

import "time"

type Data struct {
	Recipient string        `json:"recipient"`
	Severity  AlertSeverity `json:"severity"`
	Message   string        `json:"message"`
	DateTime  time.Time     `json:"date_time"`
}

type AlertSeverity string

const (
	CRITICAL AlertSeverity = "CRITICAL"
	WARNING  AlertSeverity = "WARNING"
	INFO     AlertSeverity = "INFO"
)
