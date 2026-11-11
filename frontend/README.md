# KNOWBRIDGE frontend

Next.js App Router application with TypeScript, Tailwind CSS, shadcn/ui
primitives, and a shared API client.

From the repository root, copy `frontend/.env.example` to
`frontend/.env.local`, then run:

```powershell
Set-Location frontend
npm ci
npm run dev
```

The production Docker image uses the standalone Next.js output. See the root
[development setup](../docs/setup.md) for running the complete stack.
