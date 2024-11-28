-- Sample data for the user-service

INSERT INTO organizations (org_id, name, status_id, created_at, updated_at)
VALUES (
  '53e63c81-48ae-4787-aba5-7b3015622d0a',
  'prism',
  1,
  '2024-09-19 10:00:00',
  '2024-09-19 10:00:00'
);

INSERT INTO users (
  user_id,
  org_id,
  email,
  status_id,
  created_at,
  updated_at,
  last_login
)
VALUES (
  'd5ce3efc-4fb2-48e6-891f-40fa8b6ff26c',
  '53e63c81-48ae-4787-aba5-7b3015622d0a',
  'testing@gmail.com',
  1,
  '2024-09-20 10:00:00',
  '2024-09-20 10:00:00',
  '2024-09-20 10:00:00'
);