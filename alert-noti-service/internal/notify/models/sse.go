package models

import "time"

type SSENotification struct {
	ClientID string        `json:"client_id"`
	Severity AlertSeverity `json:"severity"`
	Message  string        `json:"message"`
	DateTime time.Time     `json:"dateTime"`
}
