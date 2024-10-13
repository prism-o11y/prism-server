package data

type SourceType string

const (
	AlertNotiService SourceType = "alert-noti-service"
	LogService       SourceType = "log-service"
	UserService      SourceType = "user-service"
)
