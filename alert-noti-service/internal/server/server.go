package server

type Server struct {
}

func New() (*Server, error) {
	svr := &Server{}
	return svr, nil
}
