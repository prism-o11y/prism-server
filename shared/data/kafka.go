package data

type NotifiEvent struct {
	UserID  string
	Email   string
	Topic   string
	Message []byte
}
