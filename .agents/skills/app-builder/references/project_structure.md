# Standard A2LT Project Structure

When scaffolding a new full-stack application for the user, ALWAYS use this directory layout. It ensures a clean separation of concerns while allowing atomic full-stack commits if tracked in a single Git repository.

## The Root Layout

```text
my_awesome_project/
├── frontend/                 # Astro + Tailwind Front-End
│   ├── src/                  # All UI code
│   │   ├── components/       # Reusable Astro/Vanilla components
│   │   ├── layouts/          # Astro Layouts
│   │   ├── pages/            # Astro Routing (index.astro, etc)
│   │   └── styles/           # Global CSS (Tailwind directives)
│   ├── public/               # Static assets (images, fonts, manifest)
│   ├── package.json          # Node dependencies
│   ├── astro.config.mjs      # Astro Configuration
│   └── tailwind.config.mjs   # Tailwind Configuration
│
├── backend/                  # Django + DRF Back-End
│   ├── core/                 # Main Django project config (settings, wsgi, urls)
│   ├── apps/                 # Domain-specific Django apps (users, products, etc)
│   ├── manage.py             # Django orchestrator
│   └── requirements.txt      # Python dependencies
│
├── .gitignore                # Root gitignore covering both node_modules and .venv
└── README.md                 # Project boot guide
```

## Creating the Layout

Use bash commands to setup the root boilerplate. Wait for the user to approve directory creation before running complex setups.
