package collector

import "time"

type AlertSeverity string

const (
	Critical AlertSeverity = "CRITICAL"
	Warning  AlertSeverity = "WARNING"
	Info     AlertSeverity = "INFO"
)

type LogEntry struct {
	ClientID     string        `json:"client_id"`
	ConnectionID string        `json:"connection_id"`
	DateTime     time.Time     `json:"datetime"`
	Severity     AlertSeverity `json:"severity"`
	Message      string        `json:"message"`
}

func NewLogEntry(clientID string, connectionID string, datetime time.Time, severity AlertSeverity, message string) *LogEntry {
	return &LogEntry{
		ClientID:     clientID,
		ConnectionID: connectionID,
		DateTime:     datetime,
		Severity:     severity,
		Message:      message,
	}
}
