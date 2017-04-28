import redis
r = redis.Redis('127.0.0.1')
photo = r.get("camera:photo")
print photo
