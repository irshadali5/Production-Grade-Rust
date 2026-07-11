import sys

filepath = 'src/pages/index.astro'

with open(filepath, 'r') as f:
    content = f.read()

replacements = {
    'init_redis.sh': 'init_garnet.sh',
    'Lua script in Redis': 'Lua script in Garnet',
    'Postgres table or Redis stream': 'Postgres table or Garnet stream',
    'Distributed Redis Streams': 'Distributed Garnet Streams',
    'push to Redis,': 'push to Garnet,',
    'to a Redis Stream': 'to a Garnet Stream',
    'Redis tracks which specific': 'Garnet tracks which specific',
    'Tell Redis to permanently': 'Tell Garnet to permanently',
    '│ Postgres  │ │Redis│ │ Postmark  │': '│ Postgres  │ │Garnet││ Postmark  │',
    '<h2>Distributed Caching with Redis</h2>': '<h2>Distributed Caching with Garnet</h2>',
    "We use <strong>Redis</strong> (via the": "We use <strong>Garnet</strong> (Microsoft's highly performant, MIT-licensed datastore, via the",
    'Postgres, Redis, and OpenTelemetry': 'Postgres, Garnet, and OpenTelemetry',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(filepath, 'w') as f:
    f.write(content)

print("Redis successfully replaced with Garnet.")
