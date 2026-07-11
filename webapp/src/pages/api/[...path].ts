import { createReadStream } from 'node:fs';
import fs from 'node:fs/promises';
import path from 'node:path';
import { Hono } from 'hono';

const app = new Hono().basePath('/api');

let experimentsCache = null;

app.get('/experiments', async (c) => {
  const page = parseInt(c.req.query('page') || '1');
  const limit = parseInt(c.req.query('limit') || '50');

  if (!experimentsCache) {
    try {
      const dataPath = path.resolve(process.cwd(), '../data/experiments.json');
      const fileData = await fs.readFile(dataPath, 'utf-8');
      experimentsCache = JSON.parse(fileData);
    } catch (e) {
      console.error(e);
      return c.json({ error: 'Data not found' }, 404);
    }
  }

  const start = (page - 1) * limit;
  const end = start + limit;
  const items = experimentsCache.slice(start, end);

  return c.json({
    data: items,
    meta: {
      total: experimentsCache.length,
      page,
      limit,
      totalPages: Math.ceil(experimentsCache.length / limit),
    },
  });
});

app.get('/comments', async (c) => {
  try {
    const dataPath = path.resolve(process.cwd(), '../data/comments.txt');
    const nodeStream = createReadStream(dataPath, { start: 0, end: 10240 }); // Limit to 10KB to avoid crashing the browser

    // Convert Node stream to Web stream manually for Astro
    const webStream = new ReadableStream({
      start(controller) {
        nodeStream.on('data', (chunk) => {
          controller.enqueue(chunk);
        });
        nodeStream.on('end', () => {
          controller.close();
        });
        nodeStream.on('error', (err) => {
          controller.error(err);
        });
      },
      cancel() {
        nodeStream.destroy();
      },
    });

    return new Response(webStream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
      },
    });
  } catch (e) {
    console.error(e);
    return c.text('Not found', 404);
  }
});

export const ALL = (context) => app.fetch(context.request);
