package collector

type service struct {
	repo *repository
}

func NewService(repo *repository) *service {
	return &service{
		repo: repo,
	}
}

func (s *service) WriteLog(logSerialized []byte) error {
	return s.repo.InsertLog(logSerialized)
}
