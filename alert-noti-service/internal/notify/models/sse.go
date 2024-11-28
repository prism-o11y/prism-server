package models

import "time"

type SSENotification struct {
    ClientID      string        `json:"client_id"`
    TargetNodeID  string        `json:"target_node_id,omitempty"`
    OriginNodeID  string        `json:"origin_node_id,omitempty"`
    IsForwarded   bool          `json:"is_forwarded,omitempty"`
    Severity      AlertSeverity `json:"severity"`
    Message       string        `json:"message"`
    DateTime      time.Time     `json:"dateTime"`
}
