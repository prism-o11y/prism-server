package models

import "time"

type SMTPNotification struct {
	Recipient string        `json:"recipient"`
	Severity  AlertSeverity `json:"severity"`
	Message   string        `json:"message"`
	DateTime  time.Time     `json:"dateTime"`
}
