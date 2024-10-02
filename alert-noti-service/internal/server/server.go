package server

type Server struct{}

func New() (*Server, error) {
	return &Server{}, nil
}
