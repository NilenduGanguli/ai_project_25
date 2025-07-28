db = db.getSiblingDB('image_extractor');

db.createUser({
  user: 'extractor_user',
  pwd: 'extractor_password',
  roles: [
    {
      role: 'readWrite',
      db: 'image_extractor'
    }
  ]
});

print('Database initialized successfully'); 