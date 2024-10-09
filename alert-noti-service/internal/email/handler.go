package email

type Handler struct {
	emailSvc *service
}

func NewHandler(emailService *service) *Handler {
	return &Handler{emailSvc: emailService}
}
